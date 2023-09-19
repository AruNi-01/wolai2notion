import os

import requests

from utils import utils
from wolai.database import Database


def get_database():
    wolai_base = Database()
    wolai_conf = utils.get_yaml_data(os.path.join(wolai_base.conf_dir, 'wolai_conf.yml'))
    wolai_base.app_id = wolai_conf["base_info"]["app_id"]
    wolai_base.app_secret = wolai_conf["base_info"]["app_secret"]

    wolai_base.get_all_rows(wolai_conf['database_info']['database_id'])

    for row in wolai_base.rows:
        print(row.page_id, row.title)


if __name__ == '__main__':
    get_database()

