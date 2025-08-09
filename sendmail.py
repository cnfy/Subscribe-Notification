import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Gmail 登录信息
sender_email = "sen.yu1217@gmail.com"
app_password = "oyli brko ydlm ejth"  # 不是你的 Gmail 密码！

# 创建邮件内容
message = MIMEMultipart()
message["From"] = sender_email
message["Subject"] = "フロール新川崎募集の知らせ"



# 连接 Gmail SMTP 服务器并发送邮件
def send_gmail(time=None,receiver_email=None):
    message["To"] = receiver_email
    # 邮件正文
    body = f"当前时间：{time}\n\nフロール新川崎有新房间开始募集，请尽快前往确认。\n\n物件网址：https://www.kousha-chintai.com/search/list.php?dcd=K120162000"
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