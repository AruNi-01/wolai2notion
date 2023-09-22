from wolai.base import WolaiBase


# Page，对应 database 中的每一行
class Page(WolaiBase):
    def __init__(self):
        super().__init__()
        self.page_id = None  # 行的 page_id
        self.title = None  # 行的 title，根据此来匹配 Notion database 中的 page


