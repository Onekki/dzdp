import os
import time
import requests
from requests_html import HTMLSession

ua = "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36"
cookie = "_lxsdk_s=178717273d1-369-17c-518%7C%7C442; Hm_lpvt_602b80cf8079ae6591966cc70a3940e7=1616812978; Hm_lvt_602b80cf8079ae6591966cc70a3940e7=1616811032; ctu=5256cdb78f5755d0db3ab4716e95784664af10817e586e413064026b1b42f800; dper=34f04481c5930fede36754d1fcc0e64650cea0d81384f1039aa8e764fac5dc5991064f06a21d629a19ab780e2a4b8680dffe0730633033cd57838d935b41393b73622177538a35129161fa860e177dc6d4420922c6db4ca8b629f8b49c9d926c; dplet=2fc8f9cac19bc5dadbc069f82f035526; ll=7fd06e815b796be3df069dec7836c3df; ua=dpuser_5307947877; s_ViewType=10; _hc.v=865905b8-8f95-8d30-2aee-ee4a1c5012ef.1616811032; _lxsdk=17871727c3dc8-057e960b2adaad8-48183301-1fa400-17871727c3dc8; _lxsdk_cuid=17871727c3dc8-057e960b2adaad8-48183301-1fa400-17871727c3dc8; cy=5; cye=nanjing; fspop=test"

headers = {
    'User-Agent': ua,
    'Cookie': cookie
}

str = "User-Agent=" + ua + "&Cookie=" + cookie

a = str.split("&")

dic = {}


res = map(lambda k, v : ",".join({}), a)