import requests
from PIL import Image
from bs4 import BeautifulSoup

def auth(self):
    auth_url = "https://account.dianping.com/account/iframeLogin"
    r = self.session.get(auth_url, headers=self.get_headers())
    soup = BeautifulSoup(r.text, "lxml")

    qrcode_img_url = "https://account.dianping.com/account/getqrcodeimg"
    r = self.session.get(qrcode_img_url, headers=self.get_headers())

    qrcode_img_file = "assets/qrcode_img.png"
    with open(qrcode_img_file, "wb") as fs:
        fs.write(r.content)
    qrcode_img = Image.open(qrcode_img_file)
    qrcode_img.show()

    while True:
        qrcode_status_url = "https://account.dianping.com/account/ajax/queryqrcodestatus"
        r = self.session.post(qrcode_status_url, data=dict(self.session.cookies), headers=self.get_headers())
        result_dict = json.loads(r.text)
        status = result_dict["msg"]["status"]
        if status == 0:
            logger.warning("请扫码")
        elif status == 1:
            logger.warning("请在手机上确认")
        else:
            logger.warning("登录成功")
            break
        time.sleep(2)