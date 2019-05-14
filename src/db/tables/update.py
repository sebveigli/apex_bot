import logging
import math
import time
import pandas as pd

from db.client.mongo import Mongo

logger = logging.getLogger(__name__)

MINIMUM_TS = 0
MAXIMUM_TS = 9999999999

class Update():
    def __init__(self):
        global mongo
        mongo = Mongo('updates', 'user', True)

    @staticmethod
    def count(users=None, after=MINIMUM_TS, before=MAXIMUM_TS):
        data = mongo.get_all_data()

        df = pd.DataFrame(list(data))

        if users:
            df = df[df.user.isin(users)]

        count = 0

        for update in df.updates:
            valid_updates = [x for x in update if x['timestamp'] >= after and x['timestamp'] <= before]
            count += len(valid_updates)

        return count

    @staticmethod
    def add_user(user_id):
        data = dict(
            user=user_id,
            updates=[]
        )

        try:
            mongo.add_data(data)
        except Exception as e:
            logger.warning('Couldn\'t add user to updates DB, presumably they already exist')

    @staticmethod
    def add_update(user_id, update):
        logger.debug("Adding update for user {} to DB: {}".format(user_id, update))
        mongo.push_data_to_list('user', user_id, 'updates', update)

    @staticmethod
    def get_updates(user, after=MINIMUM_TS, before=MAXIMUM_TS):
        data = mongo.find_first('user', user)

        df = pd.DataFrame([data])

        updates = [x for x in df.updates[0] if x['timestamp'] >= after and x['timestamp'] <= before]

        return updates
    
    @staticmethod
    def get_latest_update(user):
        data = mongo.find_first('user', user)

        if len(data['updates']) == 0:
            logger.info("No updates on user {}".format(user))
            return None

        df = pd.DataFrame([data])

        return df.updates[0][-1]
