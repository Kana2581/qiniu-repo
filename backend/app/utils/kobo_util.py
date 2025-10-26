import qiniu
import requests
from qiniu import Auth

from backend.app.core.settings import settings

# =====================
# 七牛云配置
# =====================


# 认证对象
auth = Auth(settings.KOBO_ACCESS_KEY, settings.KOBO_SECRET_KEY)


# =====================
# 上传文件
# =====================
def upload_data(data:bytes, key: str, mime_type: str = "audio/mpeg") -> bool:
    """
    上传文件到七牛云
    :param data: 本地文件路径
    :param key: 上传到七牛云的文件名（带路径，例如 audios/1.mp3）
    :param mime_type: 文件类型
    :return: 上传是否成功
    """
    token = auth.upload_token(settings.KOBO_BUCKET_NAME)
    ret, info = qiniu.put_data(token, key, data, mime_type=mime_type)
    if ret is not None:
        return True
    else:
        print("上传失败:", info)
        return False


# =====================
# 生成下载链接
# =====================
def get_private_url(key: str, expires: int = 3600) -> str:
    """
    获取私有文件的下载链接
    :param key: 七牛云文件名（带路径）
    :param expires: 链接过期时间，单位秒
    :return: 私有文件下载URL
    """
    base_url = f"http://{settings.KOBO_BUCKET_DOMAIN}/{key}"
    private_url = auth.private_download_url(base_url, expires=expires)
    return private_url


# =====================
# 下载文件
# =====================
def download_file(key: str, save_path: str, expires: int = 3600) -> bool:
    """
    下载七牛云私有文件
    :param key: 七牛云文件名（带路径）
    :param save_path: 本地保存路径
    :param expires: 链接过期时间
    :return: 下载是否成功
    """
    url = get_private_url(key, expires)
    r = requests.get(url)
    if r.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(r.content)
        return True
    else:
        print("下载失败, 状态码:", r.status_code)
        return False
