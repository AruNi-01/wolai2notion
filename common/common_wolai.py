from block_convert.wolai_block import WolaiBlockContent, WolaiBlockContentType, WolaiBlockType


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
    if block.type == WolaiBlockType.IMAGE or block.type == WolaiBlockType.VIDEO:
        attach_info = block.url
    if block.type == WolaiBlockType.SIMPLE_TABLE:
        attach_info = block.table_has_header
    if block.type == WolaiBlockType.CALLOUT:
        attach_info = block.icon
    return attach_info


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
