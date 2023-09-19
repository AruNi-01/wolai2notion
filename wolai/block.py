import json

import requests

from wolai.database import Database


class Block(Database):
    # 构造函数，传入一个 dict，包含了 block 的所有信息
    def __init__(self):
        super().__init__()
        self.type = None  # block 的类型，例如 header、text 等
        self.content = []  # content 是一个 list，每个元素是一个 dict，包含了一个 block 的所有内容
        self.children_ids = []  # 如果 children_ids 为空，则表示没有子 block（普通文本）
        self.level = None  # 如果 type 是 header 类型，则 level 为 header 的级别，否则无此字段
        self.language = None    # 如果 type 是 code 类型，则 language 为代码语言，否则无此字段

    def get_all_content(self):
        content_data = []
        for item in self.content:
            content_data.append(item)
        return content_data

    def get_block_list_from_page(self, page_id):
        return self.get_block_list(page_id, True)

    def get_block_list_from_block(self, block_id):
        return self.get_block_list(block_id, False)

    # 根据 page_id 或 block_id 获取 block 列表：
    #   · 如果是 page_id，则获取该 page 的所有子 block（wolai api: GET /blocks/{id}/children)
    #   · 如果是 block_id，则获取该 block 的子 block (wolai api: GET /blocks/{id})
    def get_block_list(self, page_or_block_id, is_get_children):
        headers = {
            "Authorization": self.token
        }
        url = self.base_url + "blocks/" + page_or_block_id
        if is_get_children:
            url += "/children"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise ValueError("Request failed with status code:" + str(response.status_code))

        # 当 is_get_children=False 时，response.json()['data'] 不是数组，转为数组统一处理
        json_data = response.json()['data']
        if isinstance(json_data, list):
            data_list = json_data
        else:
            data_list = [json_data]

        block_list = []
        for json_block in data_list:
            block = Block()
            block.type = json_block['type']
            block.content = json_block['content']
            block.children_ids = json_block['children']['ids']
            if block.type == "heading":
                block.level = json_block['level']
            if block.type == "code":
                block.language = json_block['language']
            block_list.append(block)

        return block_list
