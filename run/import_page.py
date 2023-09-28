from concurrent.futures import ThreadPoolExecutor

from block_convert.wolai_block import WolaiBlockType, WolaiBlockContentType, WolaiBlockContent
from block_convert import notion_block

from notion.page import Page as NotionPage
from wolai.block import Block as WolaiBlock
from wolai.page import Page as WolaiPage
from utils import oss_client

wolai = WolaiBlock()
notion = NotionPage()
oss = None


def start_convert():
    global oss

    # 是否需要 oss 上传图片
    need_oss = input('是否需要将 wolai 的图片上传至 oss，notion 直接访问 oss (y/n): ')
    if need_oss == 'y':
        oss = oss_client.OssClient()
        print('已开启 oss 上传图片功能')

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

    for block in block_list:
        attach_info, has_children = None, False
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
        if block.children_ids:
            has_children = True

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

        insert_notion_block(block.type, wolai_block_content_list, attach_info,
                            handle_children, block.children_ids, parent_block_id_stack, parent_block_id)


def insert_notion_block(wolai_block_type, wolai_block_content_list, attach_info, handle_children, wolai_children_ids,
                        parent_block_id_stack, parent_block_id):
    """
    向 notion 中插入 block
    :param wolai_block_type: block 类型
    :param wolai_block_content_list: block 内容 list
    :param attach_info: 附加信息：
                · 当 wolai_block_type 为 heading 时，attach_info 是一个 dict，level 是 header 的级别；且当 toggle 不为 None 时 header 可折叠
                · 当 block.type 为 code 时，attach_info 为代码语言...
    :param handle_children: 是否处理子 block
    :param wolai_children_ids: 子 block 的 id list
    :param parent_block_id_stack: 由于是由父到子递归的插入 block，因此使用 stack 来记录上一个 block 的 id
    :param parent_block_id: 当前 block 的 parent_block_id
    :return:
    """

    children = []  # 调用 notion API 时的参数，用于插入子 block

    notion_block_type = notion_block.get_block_type_from_wolai(wolai_block_type, attach_info)

    # 构建 rich_text 参数
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

    children.append(children_item)

    if handle_children:  # 当处理子 block 时，parent_block_id 为上一个 block 的 id
        parent_block_id = parent_block_id_stack[-1]

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
    start_convert()
