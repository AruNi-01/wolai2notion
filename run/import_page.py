from concurrent.futures import ThreadPoolExecutor

from block_convert.wolai_block import WolaiBlockType
from block_convert import notion_block

from notion.page import Page as NotionPage
from wolai.block import Block as WolaiBlock
from wolai.page import Page as WolaiPage

from common import common_notion, common_wolai
from utils import oss_client

wolai = WolaiBlock()
notion = NotionPage()
oss = None


def start_import():
    global oss

    # 是否需要 oss 上传图片
    need_oss = input('是否需要将 wolai 的图片上传至 oss，notion 直接访问 oss (y/n): ')
    if need_oss == 'y':
        oss = oss_client.OssClient()
        print('✅ 已开启 oss 上传图片功能')
    else:
        print('❌ 未开启 oss 上传图片功能')

    max_workers = int(
        input('请输入线程池的最大线程数 (根据电脑 CPU 逻辑核数，并发执行控制台日志和 csv 数据会混乱，串行执行输入 1): '))
    with ThreadPoolExecutor(max_workers=max_workers) as t:
        for page_id in WolaiPage.get_import_page_ids():
            parent_block_id_stack = []  # 由于是由父到子递归的插入 block，因此使用 stack 来记录上一个 block 的 id
            parent_block_id = None  # 当前 block 的 parent_block_id

            # 提交任务到线程池
            future = t.submit(lambda: block_handle(page_id, parent_block_id_stack, parent_block_id, is_from_page=True))
            if future.exception() is not None:
                raise future.exception()

    t.shutdown(wait=True)  # 等待所有子线程执行完毕


def block_handle(block_id, parent_block_id_stack, parent_block_id, is_from_page=False, handle_children=False):
    """
    递归处理 block，将 block 转换为 notion 中的 block
    :param block_id: 当前处理的 block 的 id
    :param parent_block_id_stack: 由于是由父到子递归的插入 block，因此使用 stack 来记录上一个 block 的 id
    :param parent_block_id: 当前 block 的 parent_block_id
    :param is_from_page: 为 True 时说明是处理 database_row(page)，也需要匹配 notion 中的 page
    :param handle_children: 为 True 时说明是处理 block 的子 block
    :return:
    """
    global notion

    if is_from_page:
        # 根据 wolai_page_id 获取 page_meta 信息，创建 notion page
        wolai_page = WolaiPage().get_page_with_meta(block_id)
        notion = NotionPage().create_page(wolai_page)

        # 创建完 notion page 后，将其 id 赋值给 parent_block_id，用于插入它的子 block
        parent_block_id = notion.page_id

        block_list = wolai.get_block_list_from_page(block_id)
    else:
        block_list = wolai.get_block_list_from_block(block_id)

    idx, total = 0, len(block_list)
    for block in block_list:
        attach_info = common_wolai.get_attach_info(block)

        wolai_block_content_list = common_wolai.get_wolai_block_content_list(block)

        # table 内容处理
        wolai_table_content_list = []
        if block.type == WolaiBlockType.SIMPLE_TABLE:
            wolai_table_content_list = common_wolai.get_wolai_table_content_list(block)

        idx += 1
        print(f'page title【{notion.title}】，正在处理第 {idx} 个子 block，总共 {total} 个')

        insert_notion_block(block.type, wolai_block_content_list, wolai_table_content_list, attach_info,
                            handle_children, block.children_ids, parent_block_id_stack, parent_block_id)


def insert_notion_block(wolai_block_type, wolai_block_content_list, wolai_table_content_list, attach_info,
                        handle_children, wolai_children_ids, parent_block_id_stack, parent_block_id):
    """
    向 notion 中插入 block
    :param wolai_block_type: block 类型
    :param wolai_block_content_list: block 内容 list
    :param wolai_table_content_list: table 内容 list，仅当 block 类型为 table 时有值
    :param attach_info: 附加信息：
                · 当 wolai_block_type 为 heading 时，attach_info 是一个 dict，level 是 header 的级别；且当 toggle 不为 None 时 header 可折叠
                · 当 block.type 为 code 时，attach_info 为代码语言
                · 当 block.type 为 bookmark 时，attach_info 为其 url 地址
                · 当 block.type 为 image 时，attach_info 为其 url 地址
                · 当 block.type 为 table 时，attach_info 为其是否有表头
    :param handle_children: 是否处理子 block
    :param wolai_children_ids: 子 block 的 id list
    :param parent_block_id_stack: 由于是由父到子递归的插入 block，因此使用 stack 来记录上一个 block 的 id
    :param parent_block_id: 当前 block 的 parent_block_id
    :return:
    """
    notion_block_type = notion_block.get_block_type_from_wolai(wolai_block_type, attach_info)

    if handle_children:  # 当处理子 block 时，parent_block_id 为上一个 block 的 id
        parent_block_id = parent_block_id_stack[-1]

    # table 类型的 block 特殊处理
    if notion_block_type == notion_block.NotionBlockType.TABLE:
        common_notion.insert_table_block(wolai_table_content_list, attach_info, notion_block_type, notion, parent_block_id)
        return  # table 类型的 block 处理完毕，直接返回

    children_item = common_notion.build_children_item(notion_block_type, wolai_block_content_list, attach_info, oss)

    children = [children_item]  # 调用 notion API 时的参数，用于插入子 block
    try:
        response = notion.blocks.children.append(
            block_id=parent_block_id,
            **{
                "children": children
            }
        )
    except Exception as e:
        print(f'❌ 插入 block 失败 ❌，page title【{notion.title}】，原因: {e}')
        raise e

    print(f'✅ 插入 block 成功 ✅，page title【{notion.title}】')

    # 递归处理子 Block（回溯法解决父子 block 的 parent_id 问题）
    for child_id in wolai_children_ids:
        # 当插入的 block 有子 block 时，将该 block 的 id 入栈，用于插入它的子 block
        parent_block_id_stack.append(response['results'][0]['id'])
        block_handle(child_id, parent_block_id_stack, parent_block_id, handle_children=True)
        parent_block_id_stack.pop()  # 处理完一个 block 的子 block，将该 block 的 id 出栈


if __name__ == '__main__':
    start_import()
