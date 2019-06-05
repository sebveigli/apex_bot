import math
import logging
import time
import threading

from services.api import API, APITimeoutException, APIResponseFailure
from db import get_user_db, get_update_db, get_match_db

class StatUpdater(threading.Thread):
    def __init__(self, discord_client):
        super(StatUpdater, self).__init__()

        self.discord_client = discord_client

        self.running = False
        self.user_db = get_user_db()
        self.update_db = get_update_db()
        self.match_db = get_match_db()
        self.logger = logging.getLogger(__name__)

    def run(self, run_once=False):
        while True:
            self.running = True
            try:
                api = API()

                users = self.user_db.get_users()

                if users is None:
                    raise NoUsersToUpdateException()
                
                user_updates = api.uid_search(users)

                for response_tuple in user_updates:
                    user, response = response_tuple[0], response_tuple[1] 
                    previous_response = self.update_db.get_latest_update(user)

                    states = self._get_player_states(previous_response, response)
                    self._update_player_state(user, states)
                    self._update_to_db(user, states, response, previous_response)

                    if states['finish_game']:
                        self._save_match_data(user, previous_response, response)
                
                self.logger.debug("Finished updated.")

            except APITimeoutException:
                self.logger.critical("API timed out whilst doing user stat refresh.")
            except APIResponseFailure:
                self.logger.critical("API returned a non-200 status code response.")
            except NoUsersToUpdateException:
                self.logger.info('No users to update.')
            except Exception as e:
                self.logger.critical("Unhandled exception occurred: {}".format(str(e)))
            finally:
                self.running = False

                if run_once:
                    break
                time.sleep(5)

    def _get_player_states(self, previous, new):
        states = {
            "online": new['realtime']['isOnline'],
            "start_game": False,
            "finish_game": False,
            "changed_legend": False
        }
        
        if not previous:
            return states
        
        states['start_game'] = previous['realtime']['isInGame'] == 0 and new['realtime']['isInGame'] == 1
        states['finish_game'] = previous['realtime']['isInGame'] == 1 and new['realtime']['isInGame'] == 0
        states['changed_legend'] = previous['realtime']['selectedLegend'] != new['realtime']['selectedLegend']

        return states

    def _update_player_state(self, user, states, timestamp=None):
        if not timestamp:
            timestamp = math.floor(time.time())

        current_state = self.user_db.get_users([user]).iloc[0]['apex']

        if states['online'] and current_state['state'] == 'offline':
            self.logger.debug('User {} is now online.'.format(user))

            self.user_db.set_state(
                user_id=user,
                state='online',
                last_session_started=timestamp,
                timestamp=timestamp
            )

            current_state['last_session_started'] = timestamp

        if states['start_game']:
            self.logger.debug('User {} started a game of Apex.'.format(user))

            self.user_db.set_state(
                user_id=user,
                state='in_game',
                last_session_started=current_state['last_session_started'],
                timestamp=timestamp
            )
        
        if states['finish_game']:
            self.logger.debug('User {} finished a game of Apex.'.format(user))

            self.user_db.set_state(
                user_id=user,
                state='online',
                last_session_started=current_state['last_session_started'],
                timestamp=timestamp
            )
        
        if states['online'] == False and current_state['state'] in ['online', 'in_game']:
            self.logger.debug('User {} has gone offline.'.format(user))

            self.user_db.set_state(
                user_id=user,
                state='offline',
                last_session_started=current_state['last_session_started'],
                timestamp=timestamp
            )

    def _save_match_data(self, user, previous, new):
        if new['selected']['legend'] != previous['selected']['legend']:
            self.logger.warning("User {} changed legend between matches? ({} -> {})".format(
                user,
                previous['selected']['legend'],
                new['selected']['legend']
            ))
            return

        previous_stats = previous['selected']['data']
        new_stats = new['selected']['data']

        stats = {}

        for stat in new_stats:
            if previous_stats.get(stat) is not None:
                stats[stat] = new_stats[stat] - previous_stats[stat]
        
        match_data = {
            'started': previous['timestamp'],
            'ended': new['timestamp'],
            'legend': new['selected']['legend'],
            'stats': stats
        }

        self.match_db.add_match(user, match_data)
        return match_data

    def _update_to_db(self, user, states, update, previous):
        if states['start_game'] or states['finish_game'] or states['changed_legend'] or not previous:
            self.update_db.add_update(user, update)

class NoUsersToUpdateException(Exception):
    pass
