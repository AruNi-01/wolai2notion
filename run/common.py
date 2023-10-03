from block_convert import notion_block
from block_convert.wolai_block import WolaiBlockType, WolaiBlockContent, WolaiBlockContentType


def get_wolai_table_content_list(block):
    """
    获取 table block 的内容
    :param block: 表格
    :return:
    """
    wolai_table_content_list = []
    # table_content 是二维数组，需要转换为 wolai_block_content_list
    for row in block.table_content:
        cell_list = []
        for cell in row:
            text_list = []
            for text in cell['content']:
                text_list.append(_build_new_block(text))
            cell_list.append(text_list)
        wolai_table_content_list.append(cell_list)

    return wolai_table_content_list


def insert_table_block(wolai_table_content_list, attach_info, notion_block_type, notion, parent_block_id):
    """
    插入 table block
    :param wolai_table_content_list:
    :param attach_info:
    :param notion_block_type:
    :param notion:
    :param parent_block_id:
    :return:
    """
    children, row_children = [], []
    # 构建 table 的内容，notion 中 table 的每一行是一个 type 为 table_row 的 block，行的内容是 table_row 中的 cells 数组
    for row in wolai_table_content_list:
        cells = []
        for cell in row:
            cell_content = []
            for text in cell:
                cell_content_item = {
                    "type": "text",
                    "text": {
                        "content": text.content,
                        **(
                            {
                                "link": {
                                    "url": text.link
                                }
                            } if text.link is not None else {}
                        ),
                    },
                    "annotations": {
                        "bold": notion_block.rich_text_item_is_bold(text.content_type),
                        "code": notion_block.rich_text_item_is_code(text.content_type),
                    }
                }
                cell_content.append(cell_content_item)
            cells.append(cell_content)

        row_item = {
            "type": "table_row",
            "table_row": {
                "cells": cells
            }
        }
        row_children.append(row_item)

    children_item = {
        "type": notion_block_type,
        notion_block_type: {
            "has_column_header": attach_info,
            "table_width": len(wolai_table_content_list[0]),
            # table 的内容，在创建 table 时必须至少先创建一行，否则会报错，这里直接将所有行的内容都传入
            "children": row_children
        }
    }
    children.append(children_item)

    try:
        notion.blocks.children.append(
            block_id=parent_block_id,
            **{
                "children": children
            }
        )
    except Exception as e:
        print(f'❌ 插入 table 失败 ❌，原因: {e}')
        raise e

    print(f'✅ 插入 table 成功 ✅')


def get_attach_info(block):
    """
    获取 block 的附加信息
    :param block:
    :return:
    """
    attach_info = None
    # wolai block 类型
    if block.type == WolaiBlockType.HEADING:
        attach_info = {
            "level": block.level
        }
        if block.toggle:
            attach_info['toggle'] = block.toggle
    if block.type == WolaiBlockType.CODE:
        attach_info = block.language
    if block.type == WolaiBlockType.BOOKMARK:
        attach_info = block.url
    if block.type == WolaiBlockType.IMAGE:
        attach_info = block.url
    if block.type == WolaiBlockType.SIMPLE_TABLE:
        attach_info = block.table_has_header
    if block.type == WolaiBlockType.CALLOUT:
        attach_info = block.icon
    return attach_info


def get_wolai_block_content_list(block):
    """
    获取 block 中的内容
    :param block:
    :return:
    """
    wolai_block_content_list = []
    # wolai block 内容
    for text in block.content:
        wolai_block_content_list.append(_build_new_block(text))
    return wolai_block_content_list


def build_children_item(notion_block_type, wolai_block_content_list, attach_info, oss):
    """
    构建 notion block 的 children 参数
    :param notion_block_type:
    :param wolai_block_content_list:
    :param attach_info:
    :param oss:
    :return:
    """
    # 构建 rich_text 参数
    rich_text_list = []
    for wolai_block_content in wolai_block_content_list:
        rich_text_item = {
            "type": "text",
            "text": {
                "content": wolai_block_content.content,
                **(
                    {
                        "link": {
                            "url": wolai_block_content.link
                        }
                    } if wolai_block_content.link is not None else {}
                ),
            },
            "annotations": {
                "bold": notion_block.rich_text_item_is_bold(wolai_block_content.content_type),
                "code": notion_block.rich_text_item_is_code(wolai_block_content.content_type),
            }
        }
        rich_text_list.append(rich_text_item)

    # 构建 children 参数
    children_item = {
        "type": notion_block_type,
        notion_block_type: {
            "rich_text": rich_text_list
        }
    }

    # 当 attach_info 有 toggle 字段时，设置为可折叠
    if attach_info is not None and 'toggle' in attach_info and attach_info['toggle'] is True:
        children_item[notion_block_type]['is_toggleable'] = True

    # 根据 block 类型，添加/删除不同的属性
    if notion_block_type == notion_block.NotionBlockType.CODE:
        children_item[notion_block_type]['language'] = notion_block.get_code_language_from_wolai(attach_info)
    if notion_block_type == notion_block.NotionBlockType.BOOKMARK:
        del children_item[notion_block_type]['rich_text']  # bookmark 类型的 block 不需要 rich_text
        children_item[notion_block_type]['url'] = attach_info
    if notion_block_type == notion_block.NotionBlockType.DIVIDER:
        del children_item[notion_block_type]['rich_text']  # divider 类型的 block 不需要 rich_text
    if notion_block_type == notion_block.NotionBlockType.IMAGE:  # image 类型的 block 需要设置为 external 类型
        if oss is not None:
            attach_info = oss.upload_remote_image(attach_info)
        del children_item[notion_block_type]['rich_text']
        children_item[notion_block_type]['type'] = 'external'
        children_item[notion_block_type]['external'] = {
            "url": attach_info
        }
    if notion_block_type == notion_block.NotionBlockType.CALLOUT:
        children_item[notion_block_type]['icon'] = {
            "type": "emoji",
            "emoji": attach_info
        }

    return children_item


def _build_new_block(text):
    """
    构建新的 block
    :param text:
    :return:
    """
    new_block = WolaiBlockContent()
    # 注意：先判断 bold, inline_code 等是否存在，因为普通的 text，没有这些字段
    if 'bold' in text and text['bold'] is True:
        new_block.content_type = WolaiBlockContentType.BOLD
    elif 'inline_code' in text and text['inline_code'] is True:
        new_block.content_type = WolaiBlockContentType.INLINE_CODE
    else:
        new_block.content_type = WolaiBlockContentType.TEXT

    if 'link' in text:
        new_block.link = text['link']

    new_block.content = text['title']
    return new_block
