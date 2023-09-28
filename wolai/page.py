import requests

from wolai.base import WolaiBase
from utils import utils


# Page，对应 database 中的每一行
class Page(WolaiBase):
    def __init__(self):
        super().__init__()
        self.page_id = None  # 行的 page_id
        self.title = None  # 行的 title，根据此来匹配 Notion database 中的 page
        self.icon = None  # 行的 icon

    @staticmethod
    def get_import_page_ids():
        conf = utils.get_conf_data()
        return conf['wolai']['page_info']['page_ids']

    def get_page_with_meta(self, page_id):
        headers = {
            "Authorization": self.token
        }
        url = self.base_url + "blocks/" + page_id

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise ValueError("Request failed with status code:" + str(response.status_code))
        json_data = response.json()['data']

        self.page_id = page_id
        self.title = json_data['content'][0]['title']
        if 'icon' in json_data:
            self.icon = json_data['icon']['icon']

        return self
