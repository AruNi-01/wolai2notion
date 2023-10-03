# 🎭 Wolai Convert To Notion

由于 Wolai 被钉钉收购后，并未支持 Wolai 与钉钉的同步，而且官方对 Wolai 的更新频率大大降低，所以还是决定把 Wolai 的数据转移到 Notion 里。

Wolai 是直接使用官方提供的 [API](https://www.wolai.com/wolai/7FB9PLeqZ1ni9FfD11WuUi)，因为 Notion 有第三方 SDK，所以使用的是开源的 [notion-sdk-py](https://github.com/ramnes/notion-sdk-py)

## ✨ Features
- [x] Wolai Database Row(Page) 的转换
  - [x] 并发转换，提高 rows 过多时的转换速度，但 log 和 csv 会混乱
- [x] image/file 上传至 oss，然后替换 url（[Notion API 暂时不支持上传 file 到 Notion](https://developers.notion.com/reference/file-object)）
- [x] 纯 Page 的导入

支持的 Block、Block 内的 Content 类型：
```python
# Block Type
class BlockType:
    HEADING = 'heading'     # 标题，包括是否可折叠
    ENUM_LIST = 'enum_list'     # 有序列表
    BULL_LIST = 'bull_list'     # 无序列表
    TOGGLE_LIST = 'toggle_list'     # 折叠列表
    CODE = 'code'       # 代码块
    IMAGE = 'image'     # 图片
    QUOTE = 'quote'     # 引用 (markdown 中的 >)
    TEXT = 'text'       # 文本
    BOOKMARK = 'bookmark'   # 书签
    DIVIDER = 'divider'     # 分割线
    TABLE = 'table'  # 表格
    CALLOUT = 'callout'       # 标注框


# 整个大 Block 的内容中，每个 content 的类型，支持外链 link
class BlockContentType:
    BOLD = 'bold'       # 加粗文本
    INLINE_CODE = 'inline_code'     # 行内代码
    TEXT = 'text'       # 普通文本
```

## 🗳️ Database Row(Page) Convert

Database 的 property 可以直接导出为 csv，然后 import 进 Notion，row 中的内容可以使用本工具转换。

### Usage

1. 下载依赖：
    ```shell
    pip install -r requirements.txt
    ```
2. 填写配置文件 `conf/conf.yml`：
    ```yml
   wolai:
     base_info:
       app_id: xxxxxxx
       app_secret: xxxxxxxxxxx
   
     database_info:
       database_id: t8FRZDBoFmrprSZmRYywzd
   
   
   notion:
     base_info:
       secrets: xxxxxxxxxxxx
   
     database_info:
       database_id: 3db93a181d91470e852db20a04a2f1da
   
   # 若需要上传图片到 oss
   oss:
     base_info:
       access_key_id: xxxxxx
       access_key_secret: xxxxxxx
       endpoint: oss-cn-beijing.aliyuncs.com
       bucket_name: run-notion
   
     upload_info:
       # 上传到 oss bucket 的文件夹（例如 abc/efg），不包含 Bucket 名称和具体的文件名（例如 abc.jpg）。
       oss_file_path: from_wolai_img
    ```
   `base_info` 中的信息可以查看 [App 开发者中心](https://aarynlu.notion.site/aarynlu/App-34980aba84f048788b735f969742bdaa) 中对应的 API 文档；`database_info` 中的 `database_id` 可以在对应 Database 中的链接中找到（如果是把 database 嵌入一个页面的话，注意是 database_id，而不是 page_id）。
3. 运行：
    ```shell
    python ./run/convert_database_row.py
    ```
4. 运行时，会先填入需要转换的起始和结束的 idx，这个 idx 是 database 所有 row 经过 title 排序后数组的 idx，所以运行前最好先去 test 文件中看看 database rows 的 title 排序，然后填入对应的 idx。
   示例：
   ```text
   请输入从第几行(包括) database_row 开始转换 (min 0): 0
   请输入到第几行(包括) database_row 结束转换 (max 385): 5
   转换区间为 [0, 5]，总计 6 个，从【# 1004. 最大连续1的个数 III】开始, 到【#1005 K 次取反后最大化的数组和】结束
   ```
5. 运行结束后，会在 `csv_result` 文件夹中生成对应的 csv 文件，可以查看转换的结果和进度信息。

## 📑 Page Import

由于 Notion API 提供的 Create Page 接口必须要选定一个 Page 或者 Database 作为 parent（或许是我没找到直接创建新 Page 的接口），所以需要先在 Notion 新建一个页面（别忘了将 Integration 添加到该页面的 Connections 中），然后需要导入的 Wolai Page 都会导入到这个 parent 页面下，导入完成后再手动移动到 Workspace 下即可。
   
### Usage

基本步骤和上面差不多，主要是配置文件，需要填入 Notion 新建的 Parent Page ID，以及 wolai 中需要导入的 page_id：

```yaml
wolai:
  base_info:
    app_id: xxxxxxx
    app_secret: xxxxxxxxxxx

  database_info:
    database_id: t8FRZDBoFmrprSZmRYywzd

  page_info:
    parent_page_id: bc9911bac275450f965f8a4e69a60be1  # 注意：这里是 Notion 的 Parent Page ID
    page_ids:
      - gos2xG43iKy2LsRaopYmTZ
      - xmcQthUywjfNhnEqbjAWDN
```

然后运行：

```shell
python ./run/import_page.py
```

## 🙋 Questions

### Wolai API 调用频率限制

错误信息：ValueError: Request failed with status code:429

原因：Wolai API 调用频率限制，每小时只能调用 500 次

```json
{
    "message": "API调用频率过高, 请稍后再试。每小时只能调用500次",
    "error_code": 17007,
    "status_code": 429
}
```
