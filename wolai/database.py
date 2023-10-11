from wolai.base import WolaiBase
from wolai.page import Page
import requests


class Database(WolaiBase):
    def __init__(self):
        super().__init__()
        self.rows = []

    def add_row(self, row):
        self.rows.append(row)

    def get_all_rows(self, database_id):
        headers = {
            "Authorization": self.token
        }
        url = self.base_url + "databases/" + database_id
        print(f'🔍 获取 wolai_database 数据 🔍, request url: {url}')
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            raise ValueError("Request failed with status code:" + str(response.status_code))

        for row in response.json()["data"]["rows"]:
            one_row = Page()
            one_row.page_id = row["page_id"]
            one_row.title = row["data"]["title"]["value"]
            self.add_row(one_row)
