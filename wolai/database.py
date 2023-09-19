from wolai.base import WolaiBase
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
        url = self.base_url + "databases/{}".format(database_id)
        response = requests.get(url, headers=headers)
        # 检查响应状态码
        if response.status_code == 200:
            for row in response.json()["data"]["rows"]:
                one_row = Row()
                one_row.page_id = row["page_id"]
                one_row.title = row["data"]["title"]["value"]
                self.add_row(one_row)
        else:
            raise ValueError("Request failed with status code:" + str(response.status_code))


class Row(Database):
    def __init__(self):
        super().__init__()
        self.page_id = None  # 行的 page_id
        self.title = None  # 行的 title


