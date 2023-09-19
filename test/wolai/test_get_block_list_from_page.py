import os

import requests

from utils import utils
from wolai.block import Block

wolai_base = Block()
wolai_conf = utils.get_yaml_data(os.path.join(wolai_base.conf_dir, 'wolai_conf.yml'))
wolai_base.app_id = wolai_conf["base_info"]["app_id"]
wolai_base.app_secret = wolai_conf["base_info"]["app_secret"]


def get_block_list_from_page():
    wolai_base.get_all_rows(wolai_conf['database_info']['database_id'])
    page_id = wolai_base.rows[0].page_id
    block_handle(page_id, is_from_page=True)


def block_handle(page_id, is_from_page=False):
    if is_from_page:
        block_list = wolai_base.get_block_list_from_page(page_id)
    else:
        block_list = wolai_base.get_block_list_from_block(page_id)

    for block in block_list:
        print("===================block 信息==================")
        print(f'block.type: {block.type}, block.content: {block.content}, block.children_ids: {block.children_ids}')
        print("===================block 信息==================")

        # wolai block 类型
        if block.type == 'heading':     # 标题
            pass
        if block.type == 'enum_list':   # 有序列表
            pass
        if block.type == 'bull_list':   # 无序列表
            pass
        if block.type == 'code':    # 代码块
            pass
        if block.type == 'image':   # 图片
            pass
        if block.type == 'quote':   # 引用 (markdown 中的 >)
            pass
        if block.type == 'text':    # 文本
            pass

        # block 内容
        for text in block.content:
            if 'bold' in text and text['bold'] is True:
                print("加粗文本: " + text['title'])
            elif 'inline_code' in text and text['inline_code'] is True:
                print("行内代码: " + text['title'])
            else:
                print("普通文本: " + text['title'])

        # TODO: 根据上面的 block.type 和 block.content 生成的内容，将此 Block 插入到 Notion 中
        # Notion.insert(block.type, block.content)

        # 递归处理子 Block
        for child_id in block.children_ids:
            print("++++++++++++++++++++递归处理子 Block++++++++++++++++++++")
            block_handle(child_id, is_from_page=False)


if __name__ == '__main__':
    get_block_list_from_page()

