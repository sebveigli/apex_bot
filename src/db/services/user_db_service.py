import logging
import math
import time

import pandas as pd

from db.client.mongo import Mongo

logger = logging.getLogger(__name__)


class UserDBService():
    """
    Wrapper for the Users Database

    Users are a collection of dicts, containing the user's discord ID, the server IDs which they are associated with, their origin name
    and their registration date with the bot.
    """

    def __init__(self):
        global mongo
        mongo = Mongo("users", "user", True)

    @staticmethod
    def count():
        return mongo.count()

    @staticmethod
    def get_users(users=None):
        data = mongo.get_all_data()

        df = pd.DataFrame(list(data))

        if users:
            df = df[df.user.isin(users)]

        return df

    @staticmethod
    def add_user(user_id, server_id, origin_name):
        payload = dict(
            user=user_id,
            servers=[server_id],
            origin=origin_name,
            apex={"online": 0, "in_game": 0, "online_since": 0},
            registered_on=math.floor(time.time())
        )

        try:
            mongo.add_data(payload)
        except Exception as e:
            logger.warning("Couldn't add user to DB, presumably they already exist")

    @staticmethod
    def delete_user(user_id):
        mongo.delete_data("user", user_id, all=True)

    @staticmethod
    def add_server(user_id, server_id):
        mongo.push_data_to_list("user", user_id, "servers", server_id)

    @staticmethod
    def remove_server(user_id, server_id):
        mongo.remove_data_from_list("user", user_id, "servers", server_id)

    @staticmethod
    def set_origin_name(user_id, origin_name):
        mongo.update_field('user', user_id, 'origin', origin_name)
    
    @staticmethod
    def set_state(user_id, is_online, in_game, online_since):
        new_apex = {
            "online": is_online,
            "in_game": in_game,
            "online_since": online_since
        }
        mongo.update_field('user', user_id, 'apex', new_apex)
