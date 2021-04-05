import os

import requests
from bs4 import BeautifulSoup

if not os.path.exists("assets"):
    os.path.makedirs("assets")

# 南京
city_dict = {"nanjing": "http://www.dianping.com/shopall/5/0"}

for (key, value) in city_dict.items():

    html_file = "assets/" + key + ".html"
    if os.path.exists(html_file):
        continue

    r = requests.get(value)
    with open(html_file, "wb") as fs:
        fs.write(r.content)
    soup = BeautifulSoup(r.text, "lxml")
    a_list = soup.select(".list ul a")
    with open("assets/" + key + ".txt", "w") as fs:
        for a_item in a_list:
            fs.write(a_item["href"].replace("//www.dianping.com/", "") + "\n")
