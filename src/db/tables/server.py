import logging
import math
import time

import pandas as pd

from db.client.mongo import Mongo

logger = logging.getLogger(__name__)


class Server():
    def __init__(self):
        global mongo
        mongo = Mongo("servers", "server", True)

    @staticmethod
    def count():
        return mongo.count()

    @staticmethod
    def get_servers(servers=None):
        data = mongo.get_all_data()

        df = pd.DataFrame(list(data))

        if servers:
            df = df[df.server.isin(servers)]

        return df

    @staticmethod
    def add_server(server_id, owner_id, update_channel_id):
        payload = dict(
            server=server_id,
            owner=owner_id,
            admins=[owner_id],
            update_channel=update_channel_id,
            prefix="^",
            registered_on=math.floor(time.time())
        )

        try:
            mongo.add_data(payload)
        except Exception as e:
            logger.warning("Couldn't add server to DB, presumably it already exists")

    @staticmethod
    def modify_server(server_id, payload):
        mongo.replace_data("server", server_id, payload)

    @staticmethod
    def delete_server(server_id):
        mongo.delete_data("server", server_id, all=True)

    @staticmethod
    def add_admin_to_server(server_id, new_admin_id):
        mongo.push_data_to_list("server", server_id, "admins", new_admin_id)
    
    @staticmethod
    def remove_admin_from_server(server_id, id_to_revoke):
        mongo.remove_data_from_list("server", server_id, "admins", id_to_revoke)
    
    @staticmethod
    def set_prefix(server_id, prefix):
        mongo.update_field('server', server_id, "prefix", prefix)
    
    @staticmethod
    def set_owner(server_id, owner):
        mongo.update_field('server', server_id, "owner", owner)