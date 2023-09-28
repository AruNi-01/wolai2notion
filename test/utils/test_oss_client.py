from utils.oss_client import OssClient


def test_upload_local_file():
    oss_client = OssClient()
    url = oss_client.upload_local_image('/Users/aarynlu/Pictures/she.png')
    print(url)


def test_upload_remote_file():
    oss_client = OssClient()
    url = oss_client.upload_remote_image('https://secure2.wostatic.cn/static/vQS6EAeGdS5Pb92rd4K7GP/image.png?auth_key=1695880094-o5AZfATHW7ZcKw6KJZbiSH-0-9d03cda6acd8c594e9d376579a34ec68&download=image.png')
    print(url)


if __name__ == '__main__':
    # test_upload_local_file()
    test_upload_remote_file()

