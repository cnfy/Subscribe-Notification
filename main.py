import time
from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup
from logger import logger
from sendmail import send_gmail
import re

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

def start(url=None, xpath=None, receiver_email=None, target=None, task_name=None, task_id=None):
    t = getTime()
    value = getValue(url, xpath)
    if value:
        text =f"当前时间:{t}-任务ID:{task_id}-任务名称:{task_name}, 提取结果：{value}"
        if target[0] == '<' or target[0] == '>':
            num_value = int(re.search(r"\d+", value).group())
            match = re.match(r"(>=|<=|>|<)?\s*(\d+)", target)
            if match:
                operator = match.group(1) or "=="  # 默认等于
                num_target = int(match.group(2))

                # 构造表达式并比较
                if operator == ">":
                    result = num_value > num_target
                elif operator == ">=":
                    result = num_value >= num_target
                elif operator == "<":
                    result = num_value < num_target
                elif operator == "<=":
                    result = num_value <= num_target
                else:
                    result = False
            else:
                result = False
            if result:
                send_gmail(time=t, receiver_email=receiver_email)
                with open('tmp/search.txt', 'a', encoding='utf-8') as obj:
                    obj.write(text+'\n')
        else:
            if str(value) == str(target[1:]):
                send_gmail(time=t, receiver_email=receiver_email)
                with open('tmp/search.txt', 'a', encoding='utf-8') as obj:
                    obj.write(text + '\n')
    else:
        text = f"当前时间:{t}-任务ID:{task_id}-任务名称:{task_name}, 未找到目标元素，可能是动态渲染的。"
    logger.info(text)


if __name__ == '__main__':
    start()