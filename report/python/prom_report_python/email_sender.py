import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from datetime import datetime
from config_loader import config

def send_email(pdf_path):
    if not config['email']['password']:
        print("邮箱密码未设置，跳过发送邮件")
        return

    msg = MIMEMultipart()
    msg['From'] = config['email']['from']
    msg['To'] = config['email']['to']
    msg['Subject'] = f"每日监控报告 - {datetime.now().strftime('%Y-%m-%d')}"

    msg.attach(MIMEText("请查看附件中的监控日报（PDF 格式）。", 'plain', 'utf-8'))

    with open(pdf_path, "rb") as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        part.add_header('Content-Disposition', f'attachment; filename="daily_report.pdf"')
        msg.attach(part)

    server = smtplib.SMTP(config['email']['smtp_server'], config['email']['smtp_port'])
    server.starttls()
    server.login(config['email']['from'], config['email']['password'])
    server.send_message(msg)
    server.quit()
    print("邮件发送成功！")
