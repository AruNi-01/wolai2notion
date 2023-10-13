import mimetypes
from datetime import datetime
import uuid
import oss2
import requests

import utils.utils


class OssClient(object):
    def __init__(self):
        self.bucket = self._get_bucket()

    @staticmethod
    def _get_bucket():
        access_key_id = utils.utils.get_conf_data()['oss']['base_info']['access_key_id']
        access_key_secret = utils.utils.get_conf_data()['oss']['base_info']['access_key_secret']

        auth = oss2.Auth(access_key_id, access_key_secret)

        endpoint = utils.utils.get_conf_data()['oss']['base_info']['endpoint']
        bucket_name = utils.utils.get_conf_data()['oss']['base_info']['bucket_name']
        return oss2.Bucket(auth, endpoint, bucket_name)

    def upload_local_image(self, local_file_path):
        """
        上传本地图片到 oss
        :param local_file_path: 由本地文件路径加文件名包括后缀组成，例如 /users/local/myfile.txt。
        :return: 上传成功后的文件 url
        """
        # 文件名为原始文件名 + 当前时间组成
        file_name = local_file_path.split('/')[-1]
        file_suffix = file_name.split('.')[-1]
        file_name = file_name.split('.')[0] + '_' + datetime.now().strftime("%Y%m%d-%H:%M:%S:%f") + '.' + file_suffix

        self._upload_image(file_name, local_file_path)

    def upload_remote_image(self, remote_file_url):
        """
        上传远程图片到 oss
        :param remote_file_url: 远程文件 url
        :return: 上传成功后的文件 url
        """
        # 下载远程图片
        response = requests.get(remote_file_url)
        if response.status_code != 200:
            raise Exception(f'获取远程文件失败，原因：{response.text}')
        image_content = response.content

        # 获取图片类型，获取不到则默认为 jpg
        content_type = response.headers.get('Content-Type')
        extension = mimetypes.guess_extension(content_type) or '.jpg'

        # 生成唯一的文件名
        file_name = str(uuid.uuid4()) + '_' + datetime.now().strftime("%Y%m%d%H%M%S") + extension

        self._upload_image(file_name, image_content)

    def _upload_image(self, file_name, image_path_or_content):
        oss_file_path = utils.utils.get_conf_data()['oss']['upload_info']['oss_file_path']
        oss_file = str(oss_file_path) + '/' + file_name

        try:
            self.bucket.put_object(oss_file, image_path_or_content)
        except Exception as e:
            print(f'上传文件到 oss 失败，原因：{e}')
            raise e

        # https://run-notion.oss-cn-beijing.aliyuncs.com/from_wolai_img/20230928-13:45:07:044869.png
        return 'https://' + self.bucket.bucket_name + '.' + self.bucket.endpoint.split('://')[1] + '/' + oss_file
