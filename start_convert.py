import json

from block_convert.wolai_block import WolaiBlockType, WolaiBlockContentType, WolaiBlockContent
from block_convert import notion_block

from notion.database import Database as NotionDatabase
from utils import utils
from wolai.block import Block as WolaiBlock


wolai = WolaiBlock()
wolai.init_token()
notion = NotionDatabase()

PAGE_MATCH_IDX = 0  # 匹配到的 notion page 的 index，因为 database_row 都是按 title 排序的，所以可以通过该 IDX 一一对应
start_idx, end_idx = 0, 0   # 处理 database_row 的起始 index 和结束 index


def start_convert():
    global PAGE_MATCH_IDX, start_idx, end_idx

    wolai.get_all_rows(wolai.get_leetcode_database_id())
    wolai.rows.sort(key=lambda x: x.title)  # 按 title 排序，notion_rows 也是按 title 排序的，所以可以一一对应，就不用 title 去一一匹配了

    # 从控制台获取 start_idx, end_idx
    start_idx = int(input('请输入从第几行(包括) database_row 开始转换 (min 0): '))
    end_idx = int(input(f'请输入到第几行(包括) database_row 结束转换 (max {len(wolai.rows) - 1}): '))
    print(f'转换区间为 [{start_idx}, {end_idx}]，从【{wolai.rows[start_idx].title}】开始转换...')

    # 写 csv 文件表头
    utils.write_csv_row_with_convert_res(list_item=["wolai_page_id", "wolai_page_title", "top_block"])
    utils.write_csv_row_with_convert_process(list_item=["converted_rows", "total_rows"])

    for database_row in wolai.rows:
        if PAGE_MATCH_IDX < start_idx:
            PAGE_MATCH_IDX += 1
            continue
        if PAGE_MATCH_IDX > end_idx:
            break

        block_handle(database_row.page_id, is_from_page=True)
        PAGE_MATCH_IDX += 1     # 处理完一个 database_row，PAGE_MATCH_IDX + 1

        utils.write_csv_row_with_convert_res(list_item=["", "", ""])    # 写空行，用于分割不同的 database_row
        utils.write_csv_row_with_convert_process(list_item=[start_idx + 1, len(wolai.rows)])    # 写进度


def block_handle(block_id, is_from_page=False):
    """
    递归处理 block，将 block 转换为 notion 中的 block
    :param block_id:
    :param is_from_page: 为 True 时说明是处理 database_row(page)，也需要匹配 notion 中的 page
    :return:
    """

    if is_from_page:
        block_list = wolai.get_block_list_from_page(block_id)
    else:
        block_list = wolai.get_block_list_from_block(block_id)

    for block in block_list:
        print("=================== wolai block 信息 ==================")
        print(f'block.type: {block.type}, block.content: {block.content}, block.children_ids: {block.children_ids}')
        print("=================== wolai block 信息 ==================")

        attach_info = None
        # wolai block 类型
        if block.type == WolaiBlockType.HEADING:
            attach_info = block.level
        if block.type == WolaiBlockType.CODE:
            attach_info = block.language
        if block.type == WolaiBlockType.BOOKMARK:
            attach_info = block.url

        wolai_block_content_list = []
        # wolai block 内容
        for text in block.content:
            new_block = WolaiBlockContent()
            # 注意：先判断 bold, inline_code 等是否存在，因为普通的 text，没有这些字段
            if 'bold' in text and text['bold'] is True:
                new_block.content_type = WolaiBlockContentType.BOLD
            elif 'inline_code' in text and text['inline_code'] is True:
                new_block.content_type = WolaiBlockContentType.INLINE_CODE
            else:
                new_block.content_type = WolaiBlockContentType.TEXT
            new_block.content = text['title']
            wolai_block_content_list.append(new_block)

        insert_notion_block(block.type, wolai_block_content_list, attach_info, is_match_page=is_from_page)

        # 递归处理子 Block
        for child_id in block.children_ids:
            block_handle(child_id)


children = []
parent_block_id = None


def insert_notion_block(wolai_block_type, wolai_block_content_list, attach_info, is_match_page=False):
    """
    向 notion 中插入 block，
    :param wolai_block_type: block 类型
    :param wolai_block_content_list: block 内容 list
    :param attach_info: 附加信息：
                        · 当 wolai_block_type 为 heading 时，attach_info 为 header 的级别；
                        · 当 block.type 为 code 时，attach_info 为代码语言...
    :param is_match_page:
                        · 当 is_match_page 为 True 时，需要匹配 notion 中的 page，然后插入 block；
                        · 当 is_match_page 为 False 时，直接插入 block
    :return:
    """

    global children, parent_block_id
    children = []   # 每次插入 block 时，都需要清空 children，否则会额外插入上一个 block 的 children
    notion_block_type = notion_block.get_block_type_from_wolai(wolai_block_type, attach_info)

    rich_text_list = []
    for wolai_block_content in wolai_block_content_list:
        rich_text_item = {
            "type": "text",
            "text": {
                "content": wolai_block_content.content
            },
            "annotations": {
                "bold": notion_block.rich_text_item_is_bold(wolai_block_content.content_type),
                "code": notion_block.rich_text_item_is_code(wolai_block_content.content_type),
            }
        }
        rich_text_list.append(rich_text_item)

    # 获取 database 中的所有 row（page），只需要执行一次
    if not hasattr(insert_notion_block, 'has_executed'):
        print('正在获取 notion 中的所有 database row (page)...')
        notion.get_all_rows(notion.get_leetcode_database_id())
        notion.rows.sort(key=lambda x: x.title)     # 按 title 排序，wolai_rows 也是按 title 排序的，所以可以一一对应
        insert_notion_block.has_executed = True

    notion_page, wolai_page = notion.rows[PAGE_MATCH_IDX], wolai.rows[PAGE_MATCH_IDX]

    if is_match_page:   # 插入最顶层的 block
        if notion_page.title != wolai_page.title:
            raise f'wolai_page: {wolai_page.title} 与 notion_page: {notion_page.title} 不匹配'
        #
        # # 构建参数：https://developers.notion.com/reference/patch-block-children
        # children_item = {
        #     "type": notion_block_type,
        #     notion_block_type: {
        #         "rich_text": [
        #             {
        #                 "type": "text",
        #                 "text": {
        #                     "content": wolai_block_content_list[0].content  # 匹配一级标题 content
        #                 }
        #             }
        #         ],
        #         "is_toggleable": True   # 一级标题都设置 toggle
        #     }
        # }
        # children.append(children_item)
        #
        # # 插入 最顶层的 block
        # try:
        #     response = notion.blocks.children.append(
        #         block_id=notion_page.page_id,
        #         **{
        #             "children": children
        #         }
        #     )
        # except Exception as e:
        #     print(f'❌❌❌❌❌❌ 插入最顶层的 block (一级标题) 失败，database_row title 【{wolai_page.title}】，原因: {e}')
        #     raise e
        #
        # print(f'========== 插入最顶层的 block (一级标题) 完毕，response: {json.dumps(response, indent=4)}')
        #
        # parent_block_id = response['results'][0]['id']  # 获取刚插入的最顶层 block id，用于插入子 block
        #
        # utils.write_csv_row_with_convert_res(
        #     list_item=[wolai_page.page_id, wolai_page.title, wolai_block_content_list[0].content]
        # )
    else:   # 插入 block
        children_item = {
            "type": notion_block_type,
            notion_block_type: {
                "rich_text": rich_text_list
            }
        }

        if notion_block_type == notion_block.NotionBlockType.HEADING_1:
            children_item[notion_block_type]['is_toggleable'] = True
        if notion_block_type == notion_block.NotionBlockType.CODE:
            children_item[notion_block_type]['language'] = notion_block.get_code_language_from_wolai(attach_info)
        if notion_block_type == notion_block.NotionBlockType.BOOKMARK:
            del children_item[notion_block_type]['rich_text']    # bookmark 类型的 block 不需要 rich_text
            children_item[notion_block_type]['url'] = attach_info
        if notion_block_type == notion_block.NotionBlockType.DIVIDER:
            del children_item[notion_block_type]['rich_text']   # divider 类型的 block 不需要 rich_text

        children.append(children_item)

        try:
            response = notion.blocks.children.append(
                block_id=parent_block_id,   # 一级标题下面的所有 block 都是平等的，所以 parent_block_id 都是一样的
                **{
                    "children": children
                }
            )
        except Exception as e:
            print(f'❌❌❌❌❌❌ 插入子 block 失败，database_row title 【{wolai_page.title}】，原因: {e}')
            raise e

        parent_block_id = response['results'][0]['id']  # 获取刚插入的最顶层 block id，用于插入子 block

        if notion_block_type == notion_block.NotionBlockType.HEADING_1:
            utils.write_csv_row_with_convert_res(
                list_item=[wolai_page.page_id, wolai_page.title, wolai_block_content_list[0].content]
            )

        print(f'========== 插入子 block 完毕，response: {json.dumps(response, indent=4)}')


if __name__ == '__main__':
    start_convert()
