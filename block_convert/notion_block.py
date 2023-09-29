from block_convert.wolai_block import WolaiBlockType, WolaiBlockContentType


class NotionBlockType:
    HEADING_1 = 'heading_1'  # 一级标题
    HEADING_2 = 'heading_2'  # 二级标题
    HEADING_3 = 'heading_3'  # 三级标题
    NUMBERED_LIST_ITEM = 'numbered_list_item'  # 有序列表
    BULLETED_LIST_ITEM = 'bulleted_list_item'  # 无序列表
    TOGGLE = 'toggle'  # 折叠列表
    CODE = 'code'  # 代码块
    IMAGE = 'image'  # 图片
    QUOTE = 'quote'  # 引用 (markdown 中的 >)
    PARAGRAPH = 'paragraph'  # 文本段落
    BOOKMARK = 'bookmark'  # 书签
    DIVIDER = 'divider'  # 分割线
    TABLE = 'table'  # 表格


# 整个大 Block 的内容中，每个 content 的类型
class NotionBlockContentType:
    BOLD = 'bold'  # 加粗文本
    CODE = 'code'  # 行内代码
    TEXT = 'text'  # 普通文本


def get_block_type_from_wolai(wolai_block_type, attach_info):
    """
    从 wolai 的 block_type 转换为 notion 的 block_type
    :param wolai_block_type: wolai_block_type
    :param attach_info: 附加信息，例如 heading 的 level，code 的 language
    :return: notion_block_type
    """

    if wolai_block_type == WolaiBlockType.HEADING:
        if attach_info['level'] == 1:
            return NotionBlockType.HEADING_1
        elif attach_info['level'] == 2:
            return NotionBlockType.HEADING_2
        elif attach_info['level'] == 3 or attach_info['level'] == 4:
            return NotionBlockType.HEADING_3
    if wolai_block_type == WolaiBlockType.ENUM_LIST:
        return NotionBlockType.NUMBERED_LIST_ITEM
    if wolai_block_type == WolaiBlockType.BULL_LIST:
        return NotionBlockType.BULLETED_LIST_ITEM
    if wolai_block_type == WolaiBlockType.TOGGLE_LIST:
        return NotionBlockType.TOGGLE
    if wolai_block_type == WolaiBlockType.CODE:     # code language 一样，使用 attach_info 即可, 只是 notion 全是小写
        return NotionBlockType.CODE
    if wolai_block_type == WolaiBlockType.IMAGE:
        return NotionBlockType.IMAGE
    if wolai_block_type == WolaiBlockType.QUOTE:
        return NotionBlockType.QUOTE
    if wolai_block_type == WolaiBlockType.TEXT:
        return NotionBlockType.PARAGRAPH
    if wolai_block_type == WolaiBlockType.BOOKMARK:
        return NotionBlockType.BOOKMARK
    if wolai_block_type == WolaiBlockType.DIVIDER:
        return NotionBlockType.DIVIDER
    if wolai_block_type == WolaiBlockType.SIMPLE_TABLE:
        return NotionBlockType.TABLE


def get_code_language_from_wolai(wolai_code_language):
    # wolai 中的 text 对应 notion 中的 plain text；notion 中的 code language 全是小写
    return "plain text" if wolai_code_language == "text" else wolai_code_language.lower()


def rich_text_item_is_bold(wolai_block_content_type):
    return True if wolai_block_content_type == WolaiBlockContentType.BOLD else False


def rich_text_item_is_code(wolai_block_content_type):
    return True if wolai_block_content_type == WolaiBlockContentType.INLINE_CODE else False
