import json
import logging
import math
import time

import requests

from config.config import MOZAMBIQUE_HERE_API_KEY

logger = logging.getLogger(__name__)

class API():
    def __init__(self):
        self.url = ""

    def format_url(self, search_term):
        return "http://premium-api.mozambiquehe.re/bridge?version=2&platform=PC&{search_term}&auth={auth}".format(
            search_term=search_term,
            auth=MOZAMBIQUE_HERE_API_KEY
        )

    def uid_search(self, users):
        """
        Takes a DataFrame of Users, returns tuples of valid standardized responses from the API
        """
        mapped_users = zip(users["origin"].tolist(), users["user"].tolist())

        logger.debug("Getting player updates for {}".format(tuple(mapped_users)))

        self.url = self.format_url(
            search_term="uid={}".format(",".join(str(uid) for uid in users["origin"].tolist()))
        )

        return self._run(users["user"].tolist())

    def player_search(self, player_name):
        """
        Takes a single player name, returns response from the API
        """
        logger.debug("Getting single player update for {}".format(player_name))

        self.url = self.format_url(
            search_term="player={}".format(player_name),
        )

        return self._run([player_name])
    
    def _run(self, users):
        logger.debug("Sending GET to {}".format(self.url))

        try:
            response = requests.get(self.url, timeout=10)
            timestamp = math.floor(time.time())

            if response.status_code != 200:
                raise APIResponseFailure("Received failed response from Mozambiquehe.re API with status code {}".format(response.status_code))

            loaded_response = json.loads(response.text)

            if type(loaded_response) is dict:
                loaded_response = [loaded_response]

            response_tuple = list(map(self._uid_to_response_mapper, users, loaded_response))

            return self._standardize_response(response_tuple, timestamp)

        except requests.Timeout:
            raise APITimeoutException("Timeout reached whilst querying Mozambiquehe.re API")

    def _standardize_response(self, response_tuple, timestamp, remove_img_assets=True, remove_kd=True):
        logger.debug("Valid response received from API - standardizing")

        normalized = []

        for discord_uid, response in response_tuple:
            if response.get('Error'):
                continue

            selected_legend = list(response['legends']['selected'].keys())[0]

            if remove_img_assets:
                if response['legends']['selected'][selected_legend].get('ImgAssets'):
                    del response['legends']['selected'][selected_legend]['ImgAssets']

                for legend in response['legends']['all']:
                    if response['legends']['all'][legend].get('ImgAssets'):
                        del response['legends']['all'][legend]['ImgAssets']
            
            if remove_kd and response['total'].get('kd'):
                del response['total']['kd']

            for legend in response['legends']['all']:
                if not response['legends']['all'][legend].get('data'):
                    response['legends']['all'][legend]['data'] = {}
            
            normalized.append(
                [
                    discord_uid,
                    dict(
                        timestamp=timestamp,
                        legends=response['legends']['all'],
                        selected=dict(legend=selected_legend, data=response['legends']['selected'][selected_legend]),
                        realtime=response['realtime'],
                        total=response['total'],
                        profile=response['global'])
                ]
            )

        return normalized

    def _uid_to_response_mapper(self, uid, response):
        return [uid, response]

class APIResponseFailure(Exception):
    pass

class APITimeoutException(Exception):
    pass
