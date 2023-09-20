import os

from common.common_block import BlockType, BlockContentType, BlockContent
from utils import utils
from wolai.block import Block
from notion.client import NotionClient

wolai_base = Block()
wolai_conf = utils.get_yaml_data(os.path.join(wolai_base.conf_dir, 'wolai_conf.yml'))
wolai_base.app_id = wolai_conf["base_info"]["app_id"]
wolai_base.app_secret = wolai_conf["base_info"]["app_secret"]


def start_convert():
    get_block_list_from_page()


def get_block_list_from_page():
    wolai_base.get_all_rows(wolai_conf['database_info']['database_id'])
    for database_row in wolai_base.rows:
        block_handle(database_row, is_from_page=True)


def block_handle(database_row, is_from_page=False):
    if is_from_page:
        block_list = wolai_base.get_block_list_from_page(database_row.page_id)
    else:
        block_list = wolai_base.get_block_list_from_block(database_row.page_id)

    for block in block_list:
        print("===================block 信息==================")
        print(f'block.type: {block.type}, block.content: {block.content}, block.children_ids: {block.children_ids}')
        print("===================block 信息==================")

        common_block_type = None
        attach_info = None
        # wolai block 类型
        if block.type == 'heading':
            common_block_type = BlockType.HEADING
            attach_info = block.level
        if block.type == 'enum_list':
            common_block_type = BlockType.ENUM_LIST
        if block.type == 'bull_list':
            common_block_type = BlockType.BULL_LIST
        if block.type == 'code':
            common_block_type = BlockType.CODE
            attach_info = block.language
        if block.type == 'image':
            common_block_type = BlockType.IMAGE
        if block.type == 'quote':
            common_block_type = BlockType.QUOTE
        if block.type == 'text':
            common_block_type = BlockType.TEXT

        common_block_content_list = []
        # wolai block 内容
        for text in block.content:
            new_block = BlockContent()
            # 注意：先判断 bold, inline_code 等是否存在，因为普通的 text，没有这些字段
            if 'bold' in text and text['bold'] is True:
                new_block.content_type = BlockContentType.BOLD
            elif 'inline_code' in text and text['inline_code'] is True:
                new_block.content_type = BlockContentType.INLINE_CODE
            else:
                new_block.content_type = BlockContentType.TEXT
            new_block.content = text['title']
            common_block_content_list.append(new_block)

        # TODO: 根据上面的 block.type 和 block.content 生成的内容，将此 Block 插入到 Notion 中

        # attach_info 为附加信息，例如当 block.type 为 heading 时，attach_info 为 header 的级别，当 block.type 为 code 时，attach_info 为代码语言
        # Notion.insert(common_block_type, common_block_content_list, attach_info)

        # 递归处理子 Block
        for child_id in block.children_ids:
            block_handle(child_id, is_from_page=False)


if __name__ == '__main__':
    start_convert()
