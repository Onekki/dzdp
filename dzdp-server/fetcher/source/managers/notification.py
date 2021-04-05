import smtplib
from email.mime.text import MIMEText
from urllib.parse import quote

from fetcher.source import utils


class FetcherException(Exception):
    def __init__(self, data):
        super().__init__(self)
        self.data = data


class NotificationManager:
    def __init__(self):
        self.server = "smtp.qq.com"
        self.sender = "285079772@qq.com"
        self.password = "yozfkvogredbbjdi"

    def send_email(self, receivers: [], text):
        mime_text = MIMEText(text, "plain", "utf-8")
        mime_text["From"] = self.sender
        mime_text["To"] = str(receivers)
        smtp = smtplib.SMTP(self.server)
        smtp.starttls()
        smtp.login(self.sender, self.password)
        smtp.sendmail(self.sender, receivers, mime_text.as_string())
        smtp.quit()

    def send_email_update(self, receiver):
        parameter_dict = {
            "action": "update",
            "url": "https://account.dianping.com/login?redir=http%3A%2F%2Fwww.dianping.com%2F"
        }
        text = "https://onekki.com/dzdp?" + utils.dict2str(parameter_dict)
        self.send_email([receiver], text)
        raise Exception(text)

    def send_email_validate(self, receiver, url, headers):
        parameter_dict = {
            "action": "validate",
            "url": url,
            "headers": quote(str(headers))
        }
        text = "https://onekki.com/dzdp?" + utils.dict2str(parameter_dict)
        self.send_email([receiver], text)
        raise Exception(text)
