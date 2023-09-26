# Wolai Convert To Notion

由于 Wolai 被钉钉收购后，并未支持 Wolai 与钉钉的同步，而且官方对 Wolai 的更新频率大大降低，所以还是决定把 Wolai 的数据转移到 Notion 里。

Wolai 是直接使用官方提供的 [API](https://www.wolai.com/wolai/7FB9PLeqZ1ni9FfD11WuUi)，因为 Notion 有第三方 SDK，所以使用的是开源的 [notion-sdk-py](https://github.com/ramnes/notion-sdk-py)

## Features
- [x] Wolai Database Row(Page) 的转换
  - [x] Page 中 Block 父子关系的处理
  - [x] 并发转换，根据电脑的 CPU 核心输入线程数（log 和 csv 会混乱）
- [ ] 纯 Page 的转换/导入

## Database Row(Page) Convert

Database 的 property 可以直接导出为 csv，然后 import 进 Notion 即可。

本工具主要是支持 Database 中每一行，即 Page 中的内容的转换。

下面这个 LeetCode 刷题记录 Database 的转换结果：
- Wolai：https://www.wolai.com/aruni/fKuL9hqz8MhXqvcHrn31uF
- Notion：https://aarynlu.notion.site/LeetCode-5e748f5f012743ae97b12a93908c9e58?pvs=4

### Usage

1. 下载依赖：
    ```bash
    pip install -r requirements.txt
    ```
2. 填写配置文件 `conf/conf.yml`：
    ```yml
   wolai:
     base_info:
       app_id: cAjdczZs9sPsRpBf243aoi
       app_secret: 8bf139a219379d2b4d0513d2d3deb3c34db72a8d782c7f4e38f90c3d052a6638
   
     database_info:
       database_id: t8FRZDBoFmrprSZmRYywzd
   
   
   notion:
     base_info:
       secrets: secret_dLB4i2uXqHj1fDBpwNpbbINn6Mqv8iyCEPDRlYYkSE3
   
     database_info:
       database_id: 3db93a181d91470e852db20a04a2f1da
    ```
   `base_info` 中的信息可以查看 [App 开发者中心](https://aarynlu.notion.site/aarynlu/App-34980aba84f048788b735f969742bdaa) 中对应的 API 文档；`database_info` 中的 `database_id` 可以在对应 Database 中的链接中找到（如果是把 database 嵌入一个页面的话，注意是 database_id，而不是 page_id）。
3. 运行：
    ```bash
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
   

