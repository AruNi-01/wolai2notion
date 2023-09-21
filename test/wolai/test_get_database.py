from wolai.database import Database


def get_database():
    wolai_base = Database()
    wolai_base.init_token()

    wolai_base.get_all_rows(wolai_base.get_leetcode_database_id())

    for row in wolai_base.rows:
        print(row.page_id, row.title)


if __name__ == '__main__':
    get_database()

