import smtplib
from email.message import EmailMessage
import os
import mimetypes
from email.utils import formataddr

def send_mail(cfg, subject, body_text, attachments):
    # cfg is dict loaded from yaml
    send_email = cfg.get("report", {}).get("send_email", True)
    if not send_email:
        print("send_email is disabled in config. Attachments:", attachments)
        return
    smtp_cfg = cfg.get("smtp", {})
    email_cfg = cfg.get("email", {})
    host = smtp_cfg.get("host")
    port = smtp_cfg.get("port", 587)
    username = smtp_cfg.get("username")
    password = smtp_cfg.get("password")
    use_tls = smtp_cfg.get("use_tls", True)

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = formataddr((cfg.get("report", {}).get("department", ""), email_cfg.get("from")))
    msg['To'] = ", ".join(email_cfg.get("to", []))
    msg.set_content(body_text)

    for path in attachments:
        if not path or not os.path.exists(path):
            continue
        ctype, encoding = mimetypes.guess_type(path)
        if ctype is None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with open(path, "rb") as f:
            data = f.read()
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=os.path.basename(path))

    server = smtplib.SMTP(host, port, timeout=30)
    try:
        if use_tls:
            server.starttls()
        if username:
            server.login(username, password)
        server.send_message(msg)
    finally:
        server.quit()