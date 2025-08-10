import os
import logging
from requests.auth import HTTPBasicAuth
import requests

# 临时日志目录（Render 的 /tmp 是可写的）
LOG_DIR = '/tmp'
LOG_FILE = os.path.join(LOG_DIR, 'app.log')

# pCloud 配置
PCLOUD_UPLOAD_URL = 'https://api.pcloud.com/uploadfile'
ACCESS_TOKEN = os.getenv('PCLOUD_ACCESS_TOKEN')  # 从环境变量读取

# 初始化 logger
logger = logging.getLogger('render_logger')
logger.setLevel(logging.INFO)


from datetime import datetime, timedelta, timezone

# 定义 UTC+9 时区（JST）
JST = timezone(timedelta(hours=9))

# 自定义 Formatter，格式化时间为 JST
class JSTFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=JST)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return dt.isoformat()


# 避免重复添加 handler
if not logger.handlers:
    file_handler = logging.FileHandler(LOG_FILE,encoding='utf-8')
    formatter = JSTFormatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 控制台输出
    console_handler = logging.StreamHandler()
    console_formatter = JSTFormatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

def get_token():
    USERNAME = os.getenv('PCLOUD_USERNAME')
    PASSWORD = os.getenv('PCLOUD_PASSWORD')
    url = 'https://api.pcloud.com/userinfo'
    params = {
        "username": USERNAME,
        "password": PASSWORD,
        'getauth': 1
    }

    response = requests.get(url, params=params)
    data = response.json()

    auth_token = data.get("auth")
    return auth_token

def upload_log_to_pcloud():
    token = get_token()
    for file in os.listdir(LOG_DIR):
        filetmp = os.path.join(LOG_DIR, file)
        try:
            logger.info("开始上传日志到 pCloud")
            with open(filetmp, 'rb') as f:
                files = {'file': f}
                data = {
                    'auth': token,
                    'folderid': 27481362375  # 上传到根目录
                }
                response = requests.post(PCLOUD_UPLOAD_URL, files=files, data=data)
                result = response.json()
                if result.get('result') == 0:
                    logger.info("日志上传成功")
                else:
                    logger.error(f"上传失败: {result}")
        except Exception as e:
            logger.error(f"上传异常: {e}")

def update_json_to_pcloud():
    token = get_token()
    filetmp = os.path.join(LOG_DIR, 'tasks.json')
    try:
        logger.info("开始上传日志到 pCloud")
        with open(filetmp, 'rb') as f:
            files = {'file': f}
            data = {
                'auth': token,
                'folderid': 27481362375  # 上传到目录
            }
            response = requests.post(PCLOUD_UPLOAD_URL, files=files, data=data)
            result = response.json()
            if result.get('result') == 0:
                logger.info("日志上传成功")
            else:
                logger.error(f"上传失败: {result}")
    except Exception as e:
        logger.error(f"上传异常: {e}")

def download_file_from_pcloud():
    REMOTE_PATH = ['/NotificationLogs/app.log','/NotificationLogs/search.txt','/NotificationLogs/tasks.json']
    token = get_token()
    for path in REMOTE_PATH:
        save_path = os.path.join('/tmp', os.path.basename(path))
        url = 'https://api.pcloud.com/getfilelink'
        params = {
            'path': path,
            'auth': token
        }
        response = requests.get(url, params=params).json()
        durl = 'https://' + response['hosts'][0] + response['path']
        response = requests.get(durl)
        with open(save_path, 'wb') as f:
            f.write(response.content)
        logger.info(f"✅ 文件已下载到: {save_path}")


# # 启动定时任务（每 15 分钟上传一次）
# scheduler = BackgroundScheduler()
# scheduler.add_job(upload_log_to_pcloud, 'interval', minutes=15)
# scheduler.start()


if __name__ == '__main__':
    download_file_from_pcloud()