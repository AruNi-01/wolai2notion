import json

from notion_client import Client

start_cursor = None


def show_page_info():
    notion = Client(auth="secret_dLB4i2uXqHj1fDBpwNpbbINn6Mqv8iyCEPDRlYYkSE3", log_level="WARNING")

    json_page = notion.pages.retrieve(
        page_id="34980aba84f048788b735f969742bdaa",
    )

    json_page = notion.blocks.children.list(
        block_id="34980aba84f048788b735f969742bdaa",
        **{
            "start_cursor": start_cursor,
            "page_size": 100
        }
    )

    format_json = json.dumps(json_page, indent=4)
    print(format_json)


if __name__ == '__main__':
    show_page_info()
