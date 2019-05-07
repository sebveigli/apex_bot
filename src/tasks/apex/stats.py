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
        logger.debug("Doing scheduled update for Apex tracker information")

        users = USER_DB.get_users()
        updated_users = []

        timestamp = math.floor(time.time())
        valid, invalid = Stats._get_update(users)

        if len(invalid) > 0:
            logger.info("Couldn't find information for {} users, skipping them in update. {}".format(len(invalid), invalid))

        for v in valid:
            (user, response) = v[0], v[1]

            Stats._standardize_response(response, timestamp)

            (updated, state_changes) = Stats._do_update(user, response)

            if updated:
                updated_users.append([user, state_changes])

                online = 'online' in state_changes
                in_game = 'in_game' in state_changes
                online_since = 0

                if online:
                    online_since = timestamp

                USER_DB.set_state(
                    user_id=user,
                    is_online=online,
                    in_game=in_game,
                    online_since=online_since
                )
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

        all_legends_stats = response['legends']['all']
        selected_legend_stats = dict(legend=selected_legend, data=response['legends']['all'][selected_legend])
        realtime_stats = response['realtime']
        total_stats = response['total']
        global_stats = response['global']

        response = dict(
            timestamp=timestamp,
            legend_stats=all_legends_stats,
            selected_stats=selected_legend_stats,
            realtime_stats=realtime_stats,
            total_stats=total_stats,
            global_stats=global_stats
        )

    @staticmethod
    def _do_update(user, response):
        last_update = UPDATE_DB.get_latest_update(user)

        state_changes = Stats._compare_for_realtime_changes(last_update, response)

        # Check if any are true, if not then return
        if len([state for state in state_changes if state_changes[state] == True]) == 0:
            return False, None
        
        UPDATE_DB.add_update(user, response)
        return True, state_changes
    
    @staticmethod
    def _compare_for_realtime_changes(old, new):
        return dict(
            online=old['realtime']['isOnline'] == 0 and new['realtime']['isOnline'] == 1,
            offline=old['realtime']['isOnline'] == 1 and new['realtime']['isOnline'] == 0,
            in_game= new['realtime']['isInGame'] == 1,
            finished_game=old['realtime']['isInGame'] == 1 and new['realtime']['isInGame'] == 0,
        )
