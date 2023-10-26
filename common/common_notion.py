from block_convert import notion_block


def insert_notion_block(wolai_block_type, attach_info, handle_children, parent_block_id_stack,
                        parent_block_id, wolai_block_content_list, wolai_table_content_list, notion, oss):
    notion_block_type = notion_block.get_block_type_from_wolai(wolai_block_type, attach_info)

    if handle_children:  # 当处理子 block 时，parent_block_id 为上一个 block 的 id
        parent_block_id = parent_block_id_stack[-1]

    # table 类型的 block 特殊处理
    if notion_block_type == notion_block.NotionBlockType.TABLE:
        insert_table_block(wolai_table_content_list, attach_info, notion_block_type, notion, parent_block_id)
        return  # table 类型的 block 处理完毕，直接返回

    children_item = build_children_item(notion_block_type, wolai_block_content_list, attach_info, oss)

    children = [children_item]  # 调用 notion API 时的参数，用于插入子 block

    try:
        response = notion.blocks.children.append(
            block_id=parent_block_id,
            **{
                "children": children
            }
        )
    except Exception as e:
        raise e

    return response


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
            cell_content = _build_rich_text_or_table_cell_content(table_cell=cell)
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
    rich_text_list = _build_rich_text_or_table_cell_content(block_content_list=wolai_block_content_list)

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
    if notion_block_type == notion_block.NotionBlockType.CODE:  # 代码块
        children_item[notion_block_type]['language'] = notion_block.get_code_language_from_wolai(attach_info)
    if notion_block_type == notion_block.NotionBlockType.BOOKMARK:  # 书签
        del children_item[notion_block_type]['rich_text']  # bookmark 类型的 block 不需要 rich_text
        children_item[notion_block_type]['url'] = attach_info
    if notion_block_type == notion_block.NotionBlockType.DIVIDER:   # 分割线
        del children_item[notion_block_type]['rich_text']  # divider 类型的 block 不需要 rich_text
    if notion_block_type == notion_block.NotionBlockType.IMAGE:  # image 类型的 block 需要设置为 external 类型
        if oss is not None:
            attach_info = oss.upload_remote_image(attach_info)
        del children_item[notion_block_type]['rich_text']
        children_item[notion_block_type]['type'] = 'external'
        children_item[notion_block_type]['external'] = {
            "url": attach_info
        }
    if notion_block_type == notion_block.NotionBlockType.CALLOUT:   # 标注框
        children_item[notion_block_type]['icon'] = {
            "type": "emoji",
            "emoji": attach_info
        }
    if notion_block_type == notion_block.NotionBlockType.EQUATION:  # 公式
        del children_item[notion_block_type]['rich_text']
        children_item[notion_block_type]['expression'] = wolai_block_content_list[0].content

    return children_item


def _build_rich_text_or_table_cell_content(block_content_list=None, table_cell=None):
    """
    构建 block_content 的 rich_text 或 表格的每一行内容
    :param block_content_list:
    :param table_cell:
    :return: rich_text_list or table_cell_list
    """
    res_list = []
    for cell_text_or_block_content in (block_content_list if block_content_list is not None else table_cell):
        item = {
            "type": "text",
            "text": {
                "content": cell_text_or_block_content.content,
                **(
                    {
                        "link": {
                            "url": cell_text_or_block_content.link
                        }
                    } if cell_text_or_block_content.link is not None else {}
                ),
            },
            "annotations": {
                "bold": notion_block.rich_text_item_is_bold(cell_text_or_block_content.content_type),
                "code": notion_block.rich_text_item_is_code(cell_text_or_block_content.content_type),
            }
        }
        res_list.append(item)
    return res_list
