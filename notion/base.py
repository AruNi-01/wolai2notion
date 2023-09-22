import os

from utils import utils
from notion_client import Client


class NotionBase(Client):
    def __init__(self):
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.conf_dir = os.path.join(self.root_dir, 'conf')
        super().__init__(auth=self._get_secrets(), log_level="WARNING")

    def _get_secrets(self):
        config = utils.get_yaml_data(os.path.join(self.conf_dir, 'notion_conf.yml'))
        return config["base_info"]["secrets"]

    def get_leetcode_database_id(self):
        config = utils.get_yaml_data(os.path.join(self.conf_dir, 'notion_conf.yml'))
        return config["database_info"]["leetcode_database_id"]
