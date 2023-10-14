import pandas as pd
from tabulate import tabulate


def print_csv_process(csv_path):
    """
    打印 csv 进度文件
    :return:
    """
    # 读取 CSV 文件并创建表格
    df = pd.read_csv(csv_path, header=0)

    # 使用 tabulate 格式化并打印表格
    table = tabulate(df, headers="keys", showindex=False,
                     tablefmt="pipe", colalign=("center", "left", "center", "center"))

    print(f'🎉🎉🎉🎉🎉🎉🎉 转换结果 🎉🎉🎉🎉🎉🎉🎉')
    print(table)


def print_page_convert_res(success_convert_page_dict, failed_convert_page_dict):
    """
    打印 page 转换结果
    :param success_convert_page_dict:
    :param failed_convert_page_dict:
    :return:
    """
    success_list = [(k, v) for k, v in success_convert_page_dict.items()]
    failed_list = [(k, v) for k, v in failed_convert_page_dict.items()]

    success_table = tabulate(success_list, headers=["wolai_page_id", "wolai_page_title"],
                             showindex=False, tablefmt="pipe")
    failed_table = tabulate(failed_list, headers=["wolai_page_id", "wolai_page_title"],
                            showindex=False, tablefmt="pipe")

    print(f'🎉🎉🎉🎉🎉🎉🎉 转换结果 🎉🎉🎉🎉🎉🎉🎉')
    print(f'✅ 转换成功的 page ✅')
    print(success_table)
    print(' ')
    print(f'❌ 转换失败的 page ❌')
    print(failed_table)
