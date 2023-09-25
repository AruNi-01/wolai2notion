from notion.database import Database


def test_get_database_rows():
    database = Database()
    database.get_all_rows(database_id=database.get_leetcode_database_id())
    print(f'database rows num: {len(database.rows)}')

    database.rows.sort(key=lambda x: x.title)
    for row in database.rows:
        print(row.page_id + " " + row.title)


if __name__ == '__main__':
    test_get_database_rows()
