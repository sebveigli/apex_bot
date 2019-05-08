import config
import logging
import json
import math
import time
import os
import requests

from db import get_user_db, get_update_db

logger = logging.getLogger(__name__)

API_URL = "http://api.mozambiquehe.re/bridge?version=2&platform={platform}&player={players}&auth={auth}"

UPDATE_DB = get_update_db()
USER_DB = get_user_db()

class Stats():
    @staticmethod
    def scheduled_update():
        logger.debug("Doing scheduled update for user Apex data")

        users = USER_DB.get_users()
        updated_users = []

        timestamp = math.floor(time.time())
        valid, invalid = Stats._get_update(users)

        if len(invalid) > 0:
            logger.info("Couldn't find information for {} users, skipping them in update {}".format(len(invalid), invalid))

        for v in valid:
            (user, response) = v[0], v[1]

            response = Stats._standardize_response(response, timestamp)
            
            (updated, state_changes) = Stats._do_update(user, response)
            (started_session, ended_session, ended_match) = Stats._change_user_state(user, state_changes, timestamp)

            if updated:
                updated_users.append([user, state_changes])

            if started_session:
                # TODO: Create a new session
                pass

            if ended_match:
                # TODO: Save match in session
                pass
            

            if ended_session:
                # TODO: End current session
                pass
            
            
        return updated_users

    @staticmethod
    def _get_update(users):
        if len(users) == 0:
            logger.debug("No users to update")
            return
        
        players = users["origin"].tolist()
        uids = users["user"].tolist()

        player_uids_tuple = zip(players, uids)

        logger.debug('Updating users [{}]'.format(list(player_uids_tuple)))
        data = Stats._make_request(players=",".join(players))

        # API gives us back a dict if only one user queried, whilst list for multiple - normalization
        if len(users) == 1:
            data = [[uids[0], data]]
        else:
            def mapper(a, b):
                return [a, b]

            data = list(map(mapper, uids, data))
        
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
    def _make_request(players, platform="PC"):
        url = API_URL.format(platform=platform, players=players, auth=config.MOZAMBIQUE_HERE_API_KEY)

        logger.debug("Requesting to url {}".format(url))
        try:
            response = requests.get(url, timeout=15)
        except requests.Timeout:
            logger.warning("Timeout reached whilst querying Mozambiquehe.re API")
            return
        
        return json.loads(response.text)

    @staticmethod
    def _standardize_response(response, timestamp, no_internal=True, no_img_assets=True, ignore_kd=True):
        """
        Takes a response from the Mozambiquehe.re API and transforms it into the Apex Bot structure
        """
        logger.debug("Standardizing response")
        selected_legend = list(response['legends']['selected'].keys())[0]
        
        # Remove API internal data
        if no_internal:
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
    def _do_update(user, response):
        last_update = UPDATE_DB.get_latest_update(user)

        if len(last_update) == 0:
            UPDATE_DB.add_update(user, response)
            return False, None

        state_changes = Stats._compare_for_realtime_changes(last_update, response)

        # Checks for when to update to DB
        if state_changes['start_game'] or state_changes['finish_game'] or state_changes['changed_legend']:
            UPDATE_DB.add_update(user, response)
            return True, state_changes

        return False, state_changes
    
    @staticmethod
    def _compare_for_realtime_changes(old, new):
        return dict(
            online = new['realtime']['isOnline'],
            start_game = old['realtime']['isInGame'] == 0 and new['realtime']['isInGame'] == 1,
            finish_game = old['realtime']['isInGame'] == 1 and new['realtime']['isInGame'] == 0,
            changed_legend = old['realtime']['selectedLegend'] != new['realtime']['selectedLegend'],
        )

    @staticmethod
    def _change_user_state(user, state_changes, timestamp):
        started_session = False
        ended_session = False
        ended_match = False
        
        if state_changes is None:
            USER_DB.set_state(
                user_id=user,
                state='offline',
                last_session_started=None,
                timestamp=timestamp
            )
            return

        current_user_state = USER_DB.get_users([user]).iloc[0]['apex']

        if state_changes['online'] and current_user_state['state'] == 'offline':
            logger.debug("User {} is now online Apex".format(user))
            USER_DB.set_state(
                user_id=user,
                state='online',
                last_session_started=timestamp,
                timestamp=timestamp
            )

            started_session = True

        if state_changes['start_game']:
            logger.debug("User {} has started a game of Apex".format(user))
            USER_DB.set_state(
                user_id=user,
                state='in_game',
                last_session_started=current_user_state['last_session_started'],
                timestamp=timestamp
            )

        if state_changes['finish_game']:
            logger.debug("User {} has just finished a game of Apex".format(user))
            USER_DB.set_state(
                user_id=user,
                state='online',
                last_session_started=current_user_state['last_session_started'],
                timestamp=timestamp
            )

            ended_match = True

        if not state_changes['online'] and current_user_state['state'] in ['online', 'in_game']:
            logger.debug("User {} has gone offline in Apex".format(user))
            USER_DB.set_state(
                user_id=user,
                state='offline',
                last_session_started=current_user_state['last_session_started'],
                timestamp=timestamp
            )

            ended_session = True
        return started_session, ended_session, ended_match
