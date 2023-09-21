import os

from utils import utils
from notion.client import NotionClient


class MyNotionBase(NotionClient):
    def __init__(self):
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.conf_dir = os.path.join(self.root_dir, 'conf')

        super().__init__(token_v2=self._get_token_v2())
        self.base_url = "https://www.notion.so/"
        self.user_name = self._get_user_name()
        self._secret = None

    def _get_token_v2(self):
        config = utils.get_yaml_data(os.path.join(self.conf_dir, 'notion_conf.yml'))
        return config["base_info"]["token_v2"]

    def _get_user_name(self):
        config = utils.get_yaml_data(os.path.join(self.conf_dir, 'notion_conf.yml'))
        return config["base_info"]["user_name"]

    def get_leetcode_database_id(self):
        config = utils.get_yaml_data(os.path.join(self.conf_dir, 'notion_conf.yml'))
        return config["database_info"]["leetcode_database_id"]
