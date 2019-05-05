import logging
import math
import time

from db.mongo import Mongo

logger = logging.getLogger(__name__)

mongo = Mongo("users")
mongo.create_table(table_index="user", is_unique=True)

class Users():
    @staticmethod
    def get_user(user_id):
        return mongo.find_first("user", user_id)

    @staticmethod
    def add_user(user_id, server_id, origin_name):
        payload = {
            "user": user_id,
            "servers": [server_id],
            "origin_name": origin_name,
            "registered_on": math.floor(time.time())
        }

        try:
            mongo.add_data(payload)
        except Exception as e:
            logger.warning("Couldn't add user to DB, presumably they already exist.")

    @staticmethod
    def modify_user(user_id, payload):
        mongo.update_data("user", user_id, payload)

    @staticmethod
    def delete_user(user_id):
        mongo.delete_data("user", user_id, all=True)

    @staticmethod
    def add_server(user_id, server_id):
        mongo.push_data_to_list("user", user_id, "servers", server_id)