import logging
import math
import time

import pandas as pd

from db.client.mongo import Mongo

logger = logging.getLogger(__name__)


class Match():
    def __init__(self):
        global mongo
        mongo = Mongo("matches", "user", True)

    @staticmethod
    def add_user(user_id):
        data = dict(
            user=user_id,
            matches=[]
        )

        try:
            mongo.add_data(data)
        except Exception as e:
            logger.warning('Couldn\'t add user to the matches DB, presumably they already exist')

    @staticmethod
    def get_matches(user, since=None):
        data = mongo.get_all_data()

        df = pd.DataFrame(list(data))
        
        user = df[df.user == user].iloc[0]

        if since:
            return [m for m in user['matches'] if m['start'] >= since]

        return user['matches']
    
    @staticmethod
    def add_match(user, match_data):
        logger.debug("Adding match update for user {} ({})".format(user, match_data))
        mongo.push_data_to_list('user', user, 'matches', match_data)
