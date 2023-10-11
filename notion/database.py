from notion.base import NotionBase
from notion.page import Page


class Database(NotionBase):
    def __init__(self):
        super().__init__()
        self._start_cursor = None   # 请求 database 时开始的 cursor，用于分页
        self.rows = []

    def add_row(self, row):
        self.rows.append(row)

    def get_all_rows(self, database_id):
        print(f'🔍 获取 notion_database 数据 🔍，database_id: {database_id}')
        while True:
            try:
                json_page = self.databases.query(
                    **{
                        "database_id": database_id,
                        "start_cursor": self._start_cursor,
                        "page_size": 100,  # maximum page size is 100
                    }
                )
            except Exception as e:
                print(f'❌ 获取 notion_database 失败 ❌，database_id 【{database_id}】，原因: {e}')
                raise e

            for row in json_page["results"]:
                if row["properties"]["\ufeffTitle"]["title"] == []:
                    continue
                one_row = Page()
                one_row.page_id = row["id"]
                one_row.title = row["properties"]["\ufeffTitle"]["title"][0]["plain_text"]
                self.add_row(one_row)

            # 还有行数据时，更新 start_cursor，否则退出
            if json_page["has_more"]:
                self._start_cursor = json_page["next_cursor"]
            else:
                break
