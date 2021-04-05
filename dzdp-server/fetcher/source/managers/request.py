import time
import json
import requests
from requests_html import HTMLSession
from tqdm import tqdm
from logging import Logger

from fetcher.source.managers.notification import NotificationManager
from fetcher.source import utils


class RequestManager:
    def __init__(self, config, logger: Logger):
        self.assets_dir = utils.make_dirs("/assets")
        self.nfManager = NotificationManager()

        self.config = config
        self.logger = logger
        self.has_retried = False
        self.requests_number = 0
        self.sleep_time_dict = {0: 50, 1: 2, 3: 5, 10: 0}
        self.session = HTMLSession()
        self.best_sleep_time = 3

    def request_html(self, url):
        self.logger.info("url: %s", url)
        r = self.session.get(url)
        r.html.render(sleep=self.best_sleep_time)
        return r.html.html

    def request(self, url, headers=None):
        self.wait()
        self.logger.info("url: %s", url)
        if headers is None:
            headers = vars(self.config.headers)
        r = requests.get(url, headers=headers)
        if "验证中心" in r.text:
            if self.has_retried:
                self.logger.error("验证中心")
                self.logger.error(headers)
                self.nfManager.send_email_validate(self.config.email, url, headers)
            else:
                self.has_retried = True
                r = self.request(url, headers)
                self.has_retried = False
        if "页面无法访问" in r.text:
            if self.has_retried:
                self.logger.error("页面无法访问")
                self.logger.error(headers)
                self.nfManager.send_email_update(self.config.email)
            else:
                self.has_retried = True
                r = self.request(url, headers)
                self.has_retried = False
        return r

    def wait(self):
        self.requests_number += 1
        key = self.requests_number % max(self.sleep_time_dict)
        if key in self.sleep_time_dict:
            value = self.sleep_time_dict[key]
            pbar = tqdm(range(value), desc="等待" + str(value))
            for _ in pbar:
                import random
                time.sleep(1 + (random.randint(1, 100) / 1000))

    @staticmethod
    def transfer_shop_word(r_text, font_file_name_dict):
        for k_f, v_f in font_file_name_dict.items():
            with open(v_f, 'r', encoding="utf-8") as fs:
                font_dict = json.load(fs)
            for k, v in font_dict.items():
                key = str(k).replace('uni', '&#x')
                key = '"' + str(k_f) + '">' + key + ';'
                value = '"' + str(k_f) + '">' + v
                r_text = r_text.replace(key, value)
        return r_text

    @staticmethod
    def transfer_review_word(r_text, font_file_name_dict):
        directory = utils.make_dirs("/fonts")
        with open(directory + "/review-before.html", "w", encoding="utf-8") as fs:
            fs.write(r_text)
        for k_f, v_f in font_file_name_dict.items():
            with open(v_f, 'r', encoding="utf-8") as fs:
                font_dict = json.load(fs)
            for k, v in font_dict.items():
                key = str(k).replace('uni', '&#x')
                key = '"' + str(k) + '"><'
                value = '"' + str(k) + '">' + str(v) + '<'
                r_text = r_text.replace(key, value)
        with open(directory + "/review-after.html", "w", encoding="utf-8") as fs:
            fs.write(r_text)
        return r_text

    @staticmethod
    def trim_text(text):
        return text.replace("\n", "").replace("\r", "")
