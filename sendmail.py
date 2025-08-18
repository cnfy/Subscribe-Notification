import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Gmail 登录信息
sender_email = "sen.yu1217@gmail.com"
app_password = os.getenv("MAIL_PASSWORD")  # 不是你的 Gmail 密码！

# 创建邮件内容




# 连接 Gmail SMTP 服务器并发送邮件
def send_gmail(time=None,receiver_email=None, task_name=None, url=None):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["Subject"] = f"【知微】Microsight-{task_name}監視条件を満たすの知らせ"
    message["To"] = receiver_email
    # 邮件正文
    body = f"当前时间：{time}\n\n任务名称：{task_name}\n检测值已符合条件，请尽快前往确认。\n\n检测网址：{url}"
    message.attach(MIMEText(body, "plain"))


    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("✅ 邮件发送成功！")
    except Exception as e:
        print(f"❌ 邮件发送失败：{e}")

if __name__ == '__main__':
    send_gmail('2025-08-09 16:10')