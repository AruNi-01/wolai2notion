import os

import requests
from utils import utils


class WolaiBase(object):
    def __init__(self):
        self.base_url = "https://openapi.wolai.com/v1/"
        self._app_id = None
        self._app_secret = None
        self._token = None   # 在请求时，要在 Headers 头中加入 Authorization 字段，Value 为 Token（根据 app_id 和 app_secret 生成）

        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.conf_dir = os.path.join(self.root_dir, 'conf')
        
    def init_token(self):
        config = utils.get_yaml_data(os.path.join(self.conf_dir, 'wolai_conf.yml'))
        self._app_id = config["base_info"]["app_id"]
        self._app_secret = config["base_info"]["app_secret"]
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

    def get_leetcode_database_id(self):
        config = utils.get_yaml_data(os.path.join(self.conf_dir, 'wolai_conf.yml'))
        return config["database_info"]["leetcode_database_id"]
