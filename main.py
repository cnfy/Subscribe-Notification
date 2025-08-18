import time
from datetime import datetime, timedelta, timezone
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from logger import logger
from sendmail import send_gmail
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}


def getTime():
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M")

def xpath_to_css(xpath):
    parts = xpath.strip('/').split('/')
    css_parts = []
    for part in parts:
        if '[' in part:
            tag, index = part[:-1].split('[')
            css_parts.append(f"{tag}:nth-of-type({index})")
        else:
            css_parts.append(part)
    return ' > '.join(css_parts)

def is_xpath(selector):
    selector = selector.strip()
    # XPath 特征
    if selector.startswith('/') or selector.startswith('//'):
        return True
    elif '@' in selector or 'contains(' in selector or '[' in selector and not 'nth-of-type' in selector:
        return True
    else:
        return False

def getValue(url, xpath):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    if is_xpath(xpath):
        newxpath = xpath_to_css(xpath)
        target = soup.select_one(newxpath)
    else:
        target = soup.select_one(xpath)
    return target.text.strip()

def getValueV2(url, xpath):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(3000)  # 等待3秒加载
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        if is_xpath(xpath):
            newxpath = xpath_to_css(xpath)
            target = soup.select_one(newxpath)
        else:
            target = soup.select_one(xpath)
        if target:
            browser.close()
            return target.text.strip()
        else:
            logger.error("⚠️ 没找到元素")



def start(url=None, xpath=None, receiver_email=None, target=None, task_name=None, task_id=None):
    t = getTime()
    value = getValueV2(url, xpath)
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
                send_gmail(time=t, receiver_email=receiver_email, task_name=task_name, url=url)
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