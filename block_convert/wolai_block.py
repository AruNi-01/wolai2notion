# 整个大 Block 的类型
class WolaiBlockType:
    HEADING = 'heading'     # 标题
    ENUM_LIST = 'enum_list'     # 有序列表
    BULL_LIST = 'bull_list'     # 无序列表
    TOGGLE_LIST = 'toggle_list'     # 折叠列表
    CODE = 'code'       # 代码块
    IMAGE = 'image'     # 图片
    VIDEO = 'video'     # 视频
    QUOTE = 'quote'     # 引用 (markdown 中的 >)
    TEXT = 'text'       # 文本
    BOOKMARK = 'bookmark'   # 书签
    DIVIDER = 'divider'     # 分割线
    SIMPLE_TABLE = 'simple_table'   # 简单表格
    CALLOUT = 'callout'       # 标注框
    BLOCK_EQUATION = 'block_equation'   # 公式
    REFERENCE = 'reference'     # 引用


# 整个大 Block 的内容中，每个 content 的类型
class WolaiBlockContentType:
    BOLD = 'bold'       # 加粗文本
    INLINE_CODE = 'inline_code'     # 行内代码
    TEXT = 'text'       # 普通文本


class WolaiBlockContent(object):
    def __init__(self):
        self.content_type = None
        self.content = None
        self.link = None
