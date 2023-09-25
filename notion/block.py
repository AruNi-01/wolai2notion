from notion.base import NotionBase


class Block(NotionBase):
    def __init__(self):
        super().__init__()
        self.type = None

