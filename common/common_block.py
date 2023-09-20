# 整个大 Block 的类型
class BlockType:
    HEADING = 'heading'     # 标题
    ENUM_LIST = 'enum_list'     # 有序列表
    BULL_LIST = 'bull_list'     # 无序列表
    CODE = 'code'       # 代码块
    IMAGE = 'image'     # 图片
    QUOTE = 'quote'     # 引用 (markdown 中的 >)
    TEXT = 'text'       # 文本


# 整个大 Block 的内容中，每个 content 的类型
class BlockContentType:
    BOLD = 'bold'       # 加粗文本
    INLINE_CODE = 'inline_code'     # 行内代码
    TEXT = 'text'       # 普通文本


class BlockContent(object):
    def __init__(self):
        self.content_type = None
        self.content = None