import concurrent.futures
import os
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor

from block_convert.wolai_block import WolaiBlockType

from notion.database import Database as NotionDatabase
from wolai.block import Block as WolaiBlock

from common import common_notion, common_wolai, common, constants
from utils import utils, oss_client

sys.path.append(os.getcwd())

wolai = WolaiBlock()
notion = NotionDatabase()
oss = None


def start_convert():
    global oss

    print(f'正在获取 wolai 和 notion 中的所有 database_row...')
    wolai.get_all_rows(wolai.get_database_id())
    notion.get_all_rows(notion.get_database_id())
    # wolai_rows 和 notion_rows 都按 title 排序，所以可以一一对应，就不用 title 去一一匹配了
    wolai.rows.sort(key=lambda x: x.title)
    notion.rows.sort(key=lambda x: x.title)

    # 从控制台获取 start_idx, end_idx
    start_idx = int(input('请输入从第几行(包括) database_row 开始转换 (min 0): '))
    end_idx = int(input(f'请输入到第几行(包括) database_row 结束转换 (max {len(wolai.rows) - 1}): '))
    print(f'转换区间为 [{start_idx}, {end_idx}]，总计 {end_idx - start_idx + 1} 个，'
          f'从【{wolai.rows[start_idx].title}】开始, 到【{wolai.rows[end_idx].title}】结束')

    exclude_str = input("请输入以上区间中需要排除转换的 idx，元素之间用空格分隔，若无排除的则按回车键: ")
    exclude_idx_list = [int(x) for x in exclude_str.split()]
    exclude_title_list = [wolai.rows[idx].title for idx in exclude_idx_list]
    print("需要排除的 (idx, title) 如下: ")
    for item in list(zip(exclude_idx_list, exclude_title_list)):
        print(item)
        
    # 是否需要 oss 上传图片
    need_oss = input('是否需要将 wolai 的图片上传至 oss，notion 直接访问 oss (y/n): ')
    if need_oss == 'y':
        oss = oss_client.OssClient()
        print('✅ 已开启 oss 上传图片功能')
    else:
        print('❌ 未开启 oss 上传图片功能')

    # 写 csv 文件表头
    convert_process_path = utils.write_csv_row_with_convert_process(list_item=["row_idx(start_with_0)",
                                                                               "row_title(I'm_placeholder)",
                                                                               "total_idx(total_rows-1)",
                                                                               "convert_res"])

    max_workers = int(input('请输入线程池的最大线程数 (根据 CPU 核数而定），'
                            '并发执行控制台日志和 csv 数据会混乱，串行执行输入 1: '))
    with ThreadPoolExecutor(max_workers=max_workers) as t:
        futures = {}
        for idx in range(len(wolai.rows)):
            if idx < start_idx or idx in exclude_idx_list:
                continue
            if idx > end_idx:
                break

            parent_block_id_stack = []  # 由于是由父到子递归的插入 block，因此使用 stack 来记录上一个 block 的 id
            parent_block_id = notion.rows[idx].page_id  # 当前 block 的 parent_block_id

            # 提交任务到线程池
            future = t.submit(lambda: block_handle(wolai.rows[idx].page_id, idx,
                                                   parent_block_id_stack, parent_block_id, is_from_page=True))
            futures[future] = idx

    # 使用 as_completed，任务先完成的先返回
    for future in concurrent.futures.as_completed(futures):
        idx = futures[future]
        try:
            future.result()
        except Exception as e:
            print(f'❌ 转换失败 ❌，database_row idx【{idx}】, title【{wolai.rows[idx].title}】，原因: {e}')
            utils.write_csv_row_with_convert_process(list_item=[idx, wolai.rows[idx].title,
                                                                len(wolai.rows), constants.ConvertRes.FAIL])  # 写进度
            traceback.print_exc()  # 打印异常堆栈信息
            continue    # 不影响其他线程执行

        print(f'✅ 转换成功 ✅，database_row idx【{idx}】, title【{wolai.rows[idx].title}】')
        utils.write_csv_row_with_convert_process(list_item=[idx, wolai.rows[idx].title,
                                                            len(wolai.rows), constants.ConvertRes.SUCCESS])  # 写进度

    t.shutdown(wait=True)  # 等待所有子线程执行完毕

    common.print_csv_process(convert_process_path)  # 打印 csv 进度文件


def block_handle(block_id, page_match_idx, parent_block_id_stack,
                 parent_block_id, is_from_page=False, handle_children=False):
    """
    递归处理 block，将 block 转换为 notion 中的 block
    :param block_id: 当前处理的 block 的 id
    :param page_match_idx: 用于获取 page，匹配 wolai 和 notion page 的 title 是否一致
    :param parent_block_id_stack: 由于是由父到子递归的插入 block，因此使用 stack 来记录上一个 block 的 id
    :param parent_block_id: 当前 block 的 parent_block_id
    :param is_from_page: 为 True 时说明是处理 database_row(page)，也需要匹配 notion 中的 page
    :param handle_children: 为 True 时说明是处理 block 的子 block
    :return:
    """
    if is_from_page:
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
        print(f'page title【{notion.rows[page_match_idx].title}】，正在处理第 {idx} 个子 block，总共 {total} 个')
        insert_notion_block(block.type, wolai_block_content_list, wolai_table_content_list, attach_info,
                            handle_children, block.children_ids, page_match_idx, parent_block_id_stack, parent_block_id)


def insert_notion_block(wolai_block_type, wolai_block_content_list, wolai_table_content_list, attach_info,
                        handle_children, wolai_children_ids, page_match_idx, parent_block_id_stack, parent_block_id):
    """
    向 notion 中插入 block，
    :param wolai_block_type: block 类型
    :param wolai_block_content_list: block 内容 list
    :param wolai_table_content_list: table 内容 list，仅当 block 类型为 table 时有值
    :param attach_info: 附加信息：
                · 当 wolai_block_type 为 heading 时，attach_info 是一个 dict，level 是 header 的级别；且当 toggle 不为 None 时 header 可折叠
                · 当 block.type 为 code 时，attach_info 为代码语言
                · 当 block.type 为 bookmark 时，attach_info 为其 url 地址
                · 当 block.type 为 image 时，attach_info 为其 url 地址
                · 当 block.type 为 table 时，attach_info 为其是否有表头
                · 当 block.type 为 callout 时，attach_info 为其图标
                · 当 block.type 为 reference 时，attach_info 为其源 block 的 id
    :param handle_children: 是否处理子 block
    :param wolai_children_ids: 子 block 的 id list
    :param page_match_idx: 用于获取 page，匹配 wolai 和 notion page 的 title 是否一致
    :param parent_block_id_stack: 由于是由父到子递归的插入 block，因此使用 stack 来记录上一个 block 的 id
    :param parent_block_id: 当前 block 的 parent_block_id
    :return:
    """
    # 判断 title 是否匹配
    notion_page, wolai_page = notion.rows[page_match_idx], wolai.rows[page_match_idx]
    if notion_page.title != wolai_page.title:
        raise f'wolai_page: {wolai_page.title} 与 notion_page: {notion_page.title} 不匹配'

    try:
        response = common_notion.insert_notion_block(
            wolai_block_type, attach_info, handle_children, parent_block_id_stack,
            parent_block_id, wolai_block_content_list, wolai_table_content_list, notion, oss)
    except Exception as e:
        print(f'❌ 插入 block 失败 ❌，database_row idx【{page_match_idx}】, title【{wolai_page.title}】，原因: {e}')
        raise e

    print(f'✅ 插入 block 成功 ✅，database_row idx【{page_match_idx}】, title【{wolai_page.title}】')

    # 递归处理子 Block（回溯法解决父子 block 的 parent_id 问题）
    for child_id in wolai_children_ids:
        # 当插入的 block 有子 block 时，将该 block 的 id 入栈，用于插入它的子 block
        parent_block_id_stack.append(response['results'][0]['id'])
        block_handle(child_id, page_match_idx, parent_block_id_stack, parent_block_id, handle_children=True)
        parent_block_id_stack.pop()  # 处理完一个 block 的子 block，将该 block 的 id 出栈


if __name__ == '__main__':
    start_convert()
