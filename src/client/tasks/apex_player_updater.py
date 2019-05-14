import math
import logging
import time
import threading

from client.tasks.apex.stats import Stats
from db import get_user_db, get_update_db, get_match_db

class ApexPlayerUpdater(threading.Thread):
    def __init__(self):
        super(ApexPlayerUpdater, self).__init__()

        self.running = False
        self.user_db = get_user_db()
        self.update_db = get_update_db()
        self.match_db = get_match_db()

    def run(self):
        logger = logging.getLogger(__name__)

        while True:
            try:
                self.running = True
                timestamp = math.floor(time.time())

                logger.debug("Starting Apex data refresh for all users")
                users = self.user_db.get_users()

                valid, invalid = Stats.get_update(users)
                logger.debug("Valid queries {}".format(list(v[0] for v in valid)))
                logger.debug("Invalid queries {}".format(list(i for i in invalid)))

                for v in valid:
                    (user, response) = v[0], v[1]

                    current_data = Stats.standardize_response(response, timestamp)
                    previous_data = self.update_db.get_latest_update(user)

                    should_update, states = Stats.should_update_db(previous_data, current_data)

                    if should_update:
                        logger.debug("Saving data for {}".format(user))
                        self.update_db.add_update(user, current_data)

                    if states and len([s for s in states if states[s] == True]) > 0:
                        Stats.change_user_state(user, states, timestamp, self.user_db)

                        if states['finish_game']:
                            logger.debug("User {} finished a game of Apex - saving match".format(user))
                            match_data = Stats.get_match_data(user, previous_data, current_data)

                            self.match_db.add_match(user, match_data)

            except Exception as e:
                logger.critical("Error occurred whilst running ApexPlayerUpdater - {}".format(str(e)))
            finally:
                self.running = False
                time.sleep(10)
