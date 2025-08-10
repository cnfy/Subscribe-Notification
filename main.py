import time
from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup
from logger import logger
from sendmail import send_gmail

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}


def getTime():
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M")

def getValue(url, xpath):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    target = soup.select_one(xpath)
    return target.text.strip()

def start(url=None, xpath=None, receiver_email=None):
    t = getTime()
    value = getValue(url, xpath)
    if value:
        text =f"当前时间:{t},提取结果：{value}"
        if value == 1:
            send_gmail(time=t, receiver_email=receiver_email)
            with open('tmp/search.txt', 'a', encoding='utf-8') as obj:
                obj.write(text+'\n')
    else:
        text = f"当前时间:{t},未找到目标元素，可能是动态渲染的。"
    logger.info(text)


if __name__ == '__main__':
    start()