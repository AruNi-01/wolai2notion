import os

from utils import utils
from notion_client import Client


class NotionBase(Client):
    def __init__(self):
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.conf_dir = os.path.join(self.root_dir, 'conf/conf.yml')
        super().__init__(auth=self._get_secrets(), log_level="WARNING")

    @staticmethod
    def _get_secrets():
        config = utils.get_conf_data()
        return config["notion"]["base_info"]["secrets"]

    @staticmethod
    def get_leetcode_database_id():
        config = utils.get_conf_data()
        return config["notion"]["database_info"]["leetcode_database_id"]
