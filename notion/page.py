from notion.base import NotionBase


# Page，对应 database 中的每一行
class Page(NotionBase):
    def __init__(self):
        super().__init__()
        self.page_id = None  # 行的 page_id
        self.title = None  # 行的 title，根据此来匹配 database 中的 page
