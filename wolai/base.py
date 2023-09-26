import os

import requests
from utils import utils


class WolaiBase(object):
    def __init__(self):
        self.base_url = "https://openapi.wolai.com/v1/"
        self._app_id = None
        self._app_secret = None
        self._token = None   # 在请求时，要在 Headers 头中加入 Authorization 字段，Value 为 Token（根据 app_id 和 app_secret 生成）
        
    def init_token(self):
        config = utils.get_conf_data()
        self._app_id = config["wolai"]["base_info"]["app_id"]
        self._app_secret = config["wolai"]["base_info"]["app_secret"]
        self._gen_token()

    def _gen_token(self):
        if self._app_id is not None and self._app_secret is not None:
            json_data = {
                "appId": self._app_id,
                "appSecret": self._app_secret
            }
            response = requests.post(self.base_url + "token", json=json_data)

            if response.status_code != 200:
                raise ValueError("Request failed with status code:" + str(response.status_code))

            self.token = response.json()["data"]["app_token"]

    @staticmethod
    def get_database_id():
        config = utils.get_conf_data()
        return config["wolai"]["database_info"]["database_id"]
