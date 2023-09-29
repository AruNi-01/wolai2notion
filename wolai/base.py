import os

import requests
from utils import utils


class WolaiBase(object):
    def __init__(self):
        self.base_url = "https://openapi.wolai.com/v1/"
        self._app_id = None
        self._app_secret = None
        self.token = self.init_token()

    def init_token(self):
        # token cache
        if os.getenv('wolai_token') is not None:
            return os.getenv('wolai_token')

        config = utils.get_conf_data()
        self._app_id = config["wolai"]["base_info"]["app_id"]
        self._app_secret = config["wolai"]["base_info"]["app_secret"]
        if self._app_id is not None and self._app_secret is not None:
            json_data = {
                "appId": self._app_id,
                "appSecret": self._app_secret
            }
            response = requests.post(self.base_url + "token", json=json_data)

            if response.status_code != 200:
                raise ValueError("Request failed with status code:" + str(response.status_code))

            token = response.json()["data"]["app_token"]
            os.environ['wolai_token'] = token
            return token

    @staticmethod
    def get_database_id():
        config = utils.get_conf_data()
        return config["wolai"]["database_info"]["database_id"]
