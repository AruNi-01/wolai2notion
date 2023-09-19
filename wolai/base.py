import os

import requests
from utils import utils
import curlify
from pprint import pprint

proj_dir = '/Users/aarynlu/MyKB/Python/wolai2notion/'


class WolaiBase(object):
    def __init__(self):
        self.base_url = "https://openapi.wolai.com/v1/"
        self._app_id = None
        self._app_secret = None
        self._token = None   # 在请求时，要在 Headers 头中加入 Authorization 字段，Value 为 Token（根据 app_id 和 app_secret 生成）

        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.conf_dir = os.path.join(self.root_dir, 'conf')

    @property
    def app_id(self):
        return self._app_id

    @app_id.setter
    def app_id(self, app_id):
        self._app_id = app_id
        self._update_token()

    @property
    def app_secret(self):
        return self._app_secret

    @app_secret.setter
    def app_secret(self, app_secret):
        self._app_secret = app_secret
        self._update_token()

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        self._token = token

    # 当 app_id 和 app_secret 都 set 之后，自动更新 token
    def _update_token(self):
        if self.app_id is not None and self.app_secret is not None:
            json_data = {
                "appId": self.app_id,
                "appSecret": self.app_secret
            }
            response = requests.post(self.base_url + "token", json=json_data)
            # 检查响应状态码
            if response.status_code == 200:
                self.token = response.json()["data"]["app_token"]
            else:
                raise ValueError("Request failed with status code:" + str(response.status_code))
