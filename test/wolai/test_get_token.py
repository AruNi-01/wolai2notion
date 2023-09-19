import os.path

from utils import utils
from wolai.base import WolaiBase


def get_token():
    wolai_base = WolaiBase()
    wolai_conf = utils.get_yaml_data(os.path.join(wolai_base.conf_dir, 'wolai_conf.yml'))
    wolai_base.app_id = wolai_conf["base_info"]["app_id"]
    wolai_base.app_secret = wolai_conf["base_info"]["app_secret"]
    print(wolai_base.token)


if __name__ == '__main__':
    get_token()
