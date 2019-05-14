import logging
import json
import requests

from config import MOZAMBIQUE_HERE_API_KEY

logger = logging.getLogger(__name__)

API_URL_UID = "http://api.mozambiquehe.re/bridge?version=2&platform={platform}&uid={uids}&auth={auth}"
API_URL_NAME = "http://api.mozambiquehe.re/bridge?version=2&platform={platform}&player={players}&auth={auth}"

class Stats():
    @staticmethod
    def get_update(users):
        if len(users) == 0:
            logger.debug("No users to update")
            return

        origin_uids = users["origin"].tolist()
        discord_uids = users["user"].tolist()

        player_uids_tuple = zip(origin_uids, discord_uids)

        logger.debug('Updating users [{}]'.format(list(player_uids_tuple)))
        logger.debug("Origin UIDs {}".format(origin_uids))
        data = Stats.make_request(search_term=",".join(str(uid) for uid in origin_uids), uid_search=True)

        # API gives us back a dict if only one user queried, whilst list for multiple - normalization
        if len(users) == 1:
            data = [[discord_uids[0], data]]
        else:
            def mapper(a, b):
                return [a, b]

            data = list(map(mapper, discord_uids, data))

        invalid_updates = []
        valid_updates = []

        for tuple in data:
            (user, response) = tuple

            if response.get('Error'):
                logger.debug("Error retreiving stats for user {} from Mozambiquehe.re API".format(user))
                invalid_updates.append(user)
                continue

            valid_updates.append([user, response])

        return valid_updates, invalid_updates

    @staticmethod
    def make_request(search_term, uid_search=True, platform="PC"):
        if uid_search:
            url = API_URL_UID.format(platform=platform, uids=search_term, auth=MOZAMBIQUE_HERE_API_KEY)
        else:
            url = API_URL_NAME.format(platform=platform, players=search_term, auth=MOZAMBIQUE_HERE_API_KEY)

        logger.debug("Sending GET request to {}".format(url))
        try:
            response = requests.get(url, timeout=15)
        except requests.Timeout:
            logger.warning("Timeout reached whilst querying Mozambiquehe.re API")
            return

        return json.loads(response.text)

    @staticmethod
    def standardize_response(response, timestamp, no_internal=True, no_img_assets=True, ignore_kd=True):
        """
        Takes a response from the Mozambiquehe.re API and transforms it into the Apex Bot structure
        """
        logger.debug("Standardizing response")
        selected_legend = list(response['legends']['selected'].keys())[0]
        
        # Remove API internal data
        if no_internal and response.get('mozambiquehere_internal'):
            del response['mozambiquehere_internal']

        # Remove image links to legends
        if no_img_assets:
            del response['legends']['selected'][selected_legend]['ImgAssets']

            for legend in response['legends']['all']:
                del response['legends']['all'][legend]['ImgAssets']

        # Ignore KD as it's calculated by the API
        if ignore_kd:
            del response['total']['kd']
        
        # Append data key if doesn't exist for all legends to keep data normalized
        for legend in response['legends']['all']:
            if not response['legends']['all'][legend].get('data'):
                response['legends']['all'][legend]['data'] = {}

        legends = response['legends']['all']
        selected = dict(legend=selected_legend, data=response['legends']['selected'][selected_legend])
        realtime = response['realtime']
        total = response['total']
        profile = response['global']

        return dict(
            timestamp=timestamp,
            legends=legends,
            selected=selected,
            realtime=realtime,
            total=total,
            profile=profile
        )

    @staticmethod
    def should_update_db(old_data, current_data):
        if not old_data:
            return True, None

        states = dict(
            online = current_data['realtime']['isOnline'],
            start_game = old_data['realtime']['isInGame'] == 0 and current_data['realtime']['isInGame'] == 1,
            finish_game = old_data['realtime']['isInGame'] == 1 and current_data['realtime']['isInGame'] == 0,
            changed_legend = old_data['realtime']['selectedLegend'] != current_data['realtime']['selectedLegend'],
        )

        return states['start_game'] or states['finish_game'] or states['changed_legend'], states

    @staticmethod
    def change_user_state(user, state_changes, timestamp, user_db):
        started_session = False
        ended_session = False
        ended_match = False
        
        if not state_changes:
            user_db.set_state(
                user_id=user,
                state='offline',
                last_session_started=None,
                timestamp=timestamp
            )
            return

        current_user_state = user_db.get_users([user]).iloc[0]['apex']

        if state_changes['online'] and current_user_state['state'] == 'offline':
            logger.debug("User {} is now online Apex".format(user))
            user_db.set_state(
                user_id=user,
                state='online',
                last_session_started=timestamp,
                timestamp=timestamp
            )

            started_session = True

        if state_changes['start_game']:
            logger.debug("User {} has started a game of Apex".format(user))
            user_db.set_state(
                user_id=user,
                state='in_game',
                last_session_started=current_user_state['last_session_started'],
                timestamp=timestamp
            )

        if state_changes['finish_game']:
            logger.debug("User {} has just finished a game of Apex".format(user))
            user_db.set_state(
                user_id=user,
                state='online',
                last_session_started=current_user_state['last_session_started'],
                timestamp=timestamp
            )

            ended_match = True

        if not state_changes['online'] and current_user_state['state'] in ['online', 'in_game']:
            logger.debug("User {} has gone offline in Apex".format(user))
            user_db.set_state(
                user_id=user,
                state='offline',
                last_session_started=current_user_state['last_session_started'],
                timestamp=timestamp
            )

            ended_session = True
        return started_session, ended_session, ended_match

    @staticmethod
    def get_match_data(user, old_data, new_data):
        new_selected = new_data['selected']
        old_selected = old_data['selected']

        if old_selected['legend'] != new_selected['legend']:
            logger.warning("Looks like the player {} managed to change legends before match saving.. Skipping?".format(user))
            return

        stats = {}
        
        for stat in new_selected['data']:
            if old_selected['data'].get(stat):
                name = stat
                change = new_selected['data'][stat] - old_selected['data'][stat]

                stats[name] = change

        if len(stats) == 0:
            logger.warning("No new data found for the player {}, did they manage to somehow change their banners between matches?".format(user))
            return

        return {
            "started": old_data['timestamp'],
            "ended": new_data['timestamp'],
            "legend": new_selected['legend'],
            "stats": stats
        }
