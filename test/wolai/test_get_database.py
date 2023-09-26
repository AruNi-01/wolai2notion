from wolai.database import Database


def get_database():
    wolai_base = Database()

    wolai_base.get_all_rows(wolai_base.get_database_id())

    wolai_base.rows.sort(key=lambda x: x.title)
    for row in wolai_base.rows:
        print(row.page_id + " " + row.title)


if __name__ == '__main__':
    get_database()

