import requests
import json

PLATFORMS = {
    'PC': 5,
    'ORIGIN': 5, 
    'XBOX': 1,
    'PSN': 2,
    'PS4': 2
}

class ApexTrackerRetriever():
    def __init__(self, platform, name, token):
        self.api = "https://public-api.tracker.gg/apex/v1/standard/profile/%i/%s" % (PLATFORMS[platform.upper()], name)
        self.headers = {'TRN-Api-Key': token}

    def get_latest_data(self):
        return json.loads(requests.get(self.api, headers=self.headers).text)

