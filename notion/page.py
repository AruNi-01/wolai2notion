from notion.base import NotionBase
from utils import utils


# Page，对应 database 中的每一行
class Page(NotionBase):
    def __init__(self):
        super().__init__()
        self.page_id = None  # 行的 page_id
        self.title = None  # 行的 title，根据此来匹配 database 中的 page
        self.icon = None  # 行的 icon

    def create_page(self, wolai_page):
        self.title = wolai_page.title
        self.icon = wolai_page.icon

        try:
            json_page = self.pages.create(
                **{
                    "parent": {
                        "page_id": utils.get_conf_data()['wolai']['page_info']['parent_page_id']
                    },
                    **(
                        {
                            "icon": {
                                "type": "emoji",
                                "emoji": self.icon
                            }
                        }
                        if self.icon is not None else {}
                    ),
                    "properties": {
                        "title": {
                            "id": "title",
                            "type": "title",
                            "title": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": self.title
                                    },
                                }
                            ]
                        }
                    }
                }
            )
        except Exception as e:
            print(f'❌ 创建 notion_page 失败 ❌，page_title 【{self.title}】，原因: {e}')
            raise e

        self.page_id = json_page['id']
        return self
