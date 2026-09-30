# backend/application/mail_helper.py
# Minimal local-SMTP mailer (works with MailHog / `python -m smtpd -n -c DebuggingServer`)
# Never raises - a mail outage should not break the request/task that triggered it.
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import current_app as app


def send_email(to_addr, subject, body, html=False, attachment_path=None):
    if not to_addr:
        return False
    try:
        msg = MIMEMultipart()
        msg["From"] = app.config.get("SENDER_ADDRESS", "no-reply@placement-portal.local")
        msg["To"] = to_addr
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html" if html else "plain"))

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
            msg.attach(part)

        s = smtplib.SMTP(host=app.config.get("MAIL_SERVER", "localhost"),
                          port=app.config.get("MAIL_PORT", 1025), timeout=5)
        s.send_message(msg)
        s.quit()
        return True
    except Exception:
        app.logger.exception("send_email failed for %s", to_addr)
        return False


def send_gchat_webhook(text):
    """Optional: post a plain-text card to a Google Chat webhook if configured."""
    url = app.config.get("GCHAT_WEBHOOK_URL")
    if not url:
        return False
    try:
        import requests
        requests.post(url, json={"text": text}, timeout=5)
        return True
    except Exception:
        app.logger.exception("send_gchat_webhook failed")
        return False
