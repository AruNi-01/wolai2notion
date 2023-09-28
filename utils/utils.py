import os
from datetime import datetime

import yaml


root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
conf_dir = os.path.join(root_dir, 'conf/conf.yml')

current_time = datetime.now()
formatted_time = current_time.strftime("%Y-%m-%d_%H:%M:%S")

convert_res_csv_path = os.path.join(root_dir, 'csv_result/convert_res.' + formatted_time + '.csv')
convert_process_csv_path = os.path.join(root_dir, 'csv_result/convert_process.' + formatted_time + '.csv')


def get_conf_data():
    return get_yaml_data(conf_dir)


def get_yaml_data(yaml_file_path):
    with open(yaml_file_path) as f:
        yaml_data = yaml.safe_load(f)
    return yaml_data


def write_csv_row_with_convert_res(list_item):
    with open(convert_res_csv_path, 'a', encoding="utf8") as f:
        line = ",".join(str(x) for x in list_item) + "\n"
        line = line.replace(" ", "")
        f.write(line)


def write_csv_row_with_convert_process(list_item):
    with open(convert_process_csv_path, 'a', encoding="utf8") as f:
        line = ",".join(str(x) for x in list_item) + "\n"
        line = line.replace(" ", "")
        f.write(line)
