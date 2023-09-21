from urllib3 import Retry

from my_notion.base import MyNotionBase

from notion.client import NotionClient

if __name__ == '__main__':
    # Retry 构造函数的 method_whitelist 已改为 allowed_methods，因此我们自定义 Retry
    retry = Retry(
        5,
        backoff_factor=0.3,
        status_forcelist=(502, 503, 504),
        # CAUTION: adding 'POST' to this list which is not technically idempotent
        allowed_methods=(
            "POST",
            "HEAD",
            "TRACE",
            "GET",
            "PUT",
            "OPTIONS",
            "DELETE",
        ),
    )

    # Obtain the `token_v2` value by inspecting your browser cookies on a logged-in (non-guest) session on Notion.so
    client = NotionClient(
        token_v2="v02%3Auser_token_or_cookies%3A24_CGlHEfUj-i1mJcpkeU2ddGFh4pQs0ky9NGVtE9j_aD4-a9YHUsSlHjoMmyIGxPOuVfZx6CRDnVFsUh0stxoo-mBvPGSb3M9qDQY1Nv8_HT4Brb_-ySUyQ9ALlAr2N72kr",
        client_specified_retry=retry,
    )

    # Replace this URL with the URL of the page you want to edit
    page = client.get_block("https://www.notion.so/aarynlu/LeetCode-5e748f5f012743ae97b12a93908c9e58")

    print("The old title is:", page.title)

    print("page.children: ", page.space_info)

    # notion_base = MyNotionBase()
    #
    # page = notion_base.get_block(
    #     notion_base.conf_dir + notion_base.user_name + '/' + notion_base.get_leetcode_database_id())
    #
    # print("page: ", page)
