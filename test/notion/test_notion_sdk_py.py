import json

from notion_client import Client, AsyncClient


def notion_sdk_py():
    notion = Client(auth="secret_dLB4i2uXqHj1fDBpwNpbbINn6Mqv8iyCEPDRlYYkSE3", log_level="WARNING")
    async_notion = AsyncClient(auth="secret_dLB4i2uXqHj1fDBpwNpbbINn6Mqv8iyCEPDRlYYkSE3", log_level="WARNING")

    start_cursor = None
    while True:
        json_page = notion.databases.query(
            **{
                "database_id": "3db93a181d91470e852db20a04a2f1da",
                "start_cursor": start_cursor,
                "page_size": 100,  # maximum page size is 100
            }
        )
        format_json = json.dumps(json_page, indent=4)
        print(format_json)

        # 还有行数据时，更新 start_cursor，否则退出
        if json_page["has_more"]:
            start_cursor = json_page["next_cursor"]
        else:
            break


if __name__ == '__main__':
    notion_sdk_py()
