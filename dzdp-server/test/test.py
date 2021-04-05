import os
import re
import sys
import json
import requests
from collections import Counter

ua = "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36"
cookie = "_lxsdk_s=178717273d1-369-17c-518%7C%7C442; Hm_lpvt_602b80cf8079ae6591966cc70a3940e7=1616812978; Hm_lvt_602b80cf8079ae6591966cc70a3940e7=1616811032; ctu=5256cdb78f5755d0db3ab4716e95784664af10817e586e413064026b1b42f800; dper=34f04481c5930fede36754d1fcc0e64650cea0d81384f1039aa8e764fac5dc5991064f06a21d629a19ab780e2a4b8680dffe0730633033cd57838d935b41393b73622177538a35129161fa860e177dc6d4420922c6db4ca8b629f8b49c9d926c; dplet=2fc8f9cac19bc5dadbc069f82f035526; ll=7fd06e815b796be3df069dec7836c3df; ua=dpuser_5307947877; s_ViewType=10; _hc.v=865905b8-8f95-8d30-2aee-ee4a1c5012ef.1616811032; _lxsdk=17871727c3dc8-057e960b2adaad8-48183301-1fa400-17871727c3dc8; _lxsdk_cuid=17871727c3dc8-057e960b2adaad8-48183301-1fa400-17871727c3dc8; cy=5; cye=nanjing; fspop=test"

headers = {
    'User-Agent': ua,
    'Cookie': cookie
}

class Word():
    def __init__(self, name, x, y):
        self.name = name
        self.x = int(float(x))
        self.y = int(float(y))
    
    def __str__(self):
        return "name: %s, x: %s, y %s" % (self.name, self.x, self.y)
    def __repr__(self):
        return self.__str__()


class WordParser():
    def __init__(self):
        self._offset_x = None
        self._offset_y = None
    
    def parse(self, svg_text, word: Word):
        
        transfer_tuple_list =  self._read_transfer_tuple_list(svg_text)
        transfer_dict = dict(transfer_tuple_list)

        row_key = str(word.y + self._offset_y)
        col_index = (word.x + self._offset_x) // 14

        return transfer_dict[row_key][col_index]
    
    def _read_transfer_tuple_list(self, svg_text):
        self._offset_x = 0
        if "#333" in svg_text:
            self._offset_y = 23
        elif "#666" in svg_text:
            self._offset_y = 15
        else:
            logger.error("解析规则改变")
            sys.exit()
        transfer_tuple_list = None
        if "textPath" in svg_text:
            y_tuple_list = re.findall('<path id=".*?" d="M0 (.*?) H600"/>', svg_text)
            value_tuple_list = re.findall('>(.*?)</textPath>', svg_text)
            transfer_tuple_list = list(zip(y_tuple_list, value_tuple_list))
        else:
            transfer_tuple_list = re.findall('<text x=".*?" y="(.*?)">(.*?)</text>', svg_text)
        # 也许还有其他解析规则
        return transfer_tuple_list
    
    @staticmethod
    def get_words(css_text):
        first = re.search("^.(.*?){", css_text).group(1)
        word_tuple_list = re.findall(".(.{" + str(len(first)) + "}?)\{background:-(.*?)px -(.*?)px;}", css_text, re.S)
        words = []
        for (name, x, y) in word_tuple_list:
            word = Word(name, x, y)
            words.append(word)

        with open("test/words.txt", "w") as fs:
            fs.writelines(str(words))
        return words


    @staticmethod
    def download(shop_id):
        review_page_file = "test/" + shop_id + ".html"

        if not os.path.exists(review_page_file):
            review_page_url = "http://www.dianping.com/shop/" + shop_id + "/review_all"
            logger.warning("review_page_url: %s", review_page_url)
            r = requests.get(review_page_url, headers=headers)

            with open(review_page_file, "wb") as fs:
                fs.write(r.content)
        
        with open(review_page_file, "r") as fs:
            review_page_text = fs.read()

        css_file = "test/" + shop_id + ".css"
        if not os.path.exists(css_file):
            css_url = "https:" + re.findall(' href="(//s3plus.meituan.net/v1/.*?)">', review_page_text)[0]
            logger.warning("css_url: %s", css_url)
            r = requests.get(css_url)

            with open(css_file, "wb") as fs:
                fs.write(r.content)

            with open(css_file + ".raw", "wb") as fs:
                fs.write(r.content)
        
        with open(css_file, "r") as fs:
            css_text = fs.read()

        type_tuple_list = re.findall('\[class\^="(.*?)"\].*?url\((//s3plus.meituan.net/v1/.*?)\)', css_text, re.S)
        for type_tuple in type_tuple_list:
            (type, type_url) = type_tuple
            logger.warning(type + "-url: %s", type_url)
            type_file = "test/svg-" + type + ".xml"
            if os.path.exists(type_file):
                continue
            r = requests.get("https:" + type_url)
            with open(type_file, "wb") as fs:
                fs.write(r.content)

    # 计算偏移
    @staticmethod
    def calculate(shop_id):
        
        css_file = "test/" + shop_id + ".css"
        with open(css_file + ".raw", 'r') as fs:
            css_text = fs.read()

        words = WordParser.get_words(css_text)
        type_tuple_list = re.findall('\[class\^="(.*?)"\].*?url\((//s3plus.meituan.net/v1/.*?)\)', css_text, re.S)
        same_x = {}
        same_y = {}
        for type_tuple in type_tuple_list:
            (type, type_url) = type_tuple

            type_file = "test/svg-" + type + ".xml"
            with open(type_file, 'r') as fs:
                svg_text = fs.read()

            for word in words:
                if word.name[:len(type)] not in same_x:
                    same_x[word.name[:len(type)]] = []
                    same_y[word.name[:len(type)]] = []
                same_x[word.name[:len(type)]].append(word.x)
                same_y[word.name[:len(type)]].append(word.y)
            # logger.warning(type, "x", len(set(same_x[type])), set(same_x[type]))
            # for item in set(same_x[type]):
            #     logger.warning("%3d 重复 %3d" %(item, same_x[type].count(item)))
            for item in set(same_y[type]):
                # logger.warning("%5d 重复 %3d" %(item, same_y[type].count(item)))
                pass
            d = sorted(Counter(same_y[type]).items(), key=lambda x: x[1])

            logger.warning("=================")

            logger.warning("%s %s", type, d)

            logger.warning("-------------")

            parser = WordParser()
            transfer_tuple_list = parser._read_transfer_tuple_list(svg_text)
            len_list = []
            for transfer_tuple in transfer_tuple_list:
                (y, row) = transfer_tuple
                len_list.append((y, len(row)))
            
            logger.warning(sorted(len_list, key=lambda x: x[1]))

            logger.warning("=================")
    
    @staticmethod
    def dump():
        parser = WordParser()
        word_transfer_dict = {}

        css_file = "test/" + shop_id + ".css"
        with open(css_file + ".raw", 'r') as fs:
            css_text = fs.read()

        words = WordParser.get_words(css_text)



        type_tuple_list = re.findall('\[class\^="(.*?)"\].*?url\((//s3plus.meituan.net/v1/.*?)\)', css_text, re.S)
        for type_tuple in type_tuple_list:
            (type, type_url) = type_tuple

            type_file = "test/svg-" + type + ".xml"
            with open(type_file, 'r') as fs:
                svg_text = fs.read()


            with open("test/words-" + type + ".txt", "w") as fs:
                fs.writelines(str(words))

            for word in words:
                if ("riage" == word.name):
                    logger.warning("is in %s", word)
                if type != word.name[:len(type)]:
                    continue
                word_transfer_dict[word.name] = parser.parse(svg_text, word)
            with open(type_file.replace(".xml", ".json"), "w", encoding="utf-8") as fs:
                json.dump(word_transfer_dict, fs, ensure_ascii=False)
        

    @staticmethod
    def test(name, x, y):
        word = Word(name, x, y)
        parser = WordParser()

        type = name[:2]
        logger.warning("%s %s", word, type)
        type_file = "test/svg-" + type + ".xml"
        with open(type_file, 'r') as fs:
            svg_text = fs.read()
        logger.warning(parser.parse(svg_text, word))



shop_id = "l9FopTwWworZHsKi"

# 下载

# WordParser.download(shop_id)


# 计算

# WordParser.calculate(shop_id)


# 转换

# WordParser.dump()


# 测试

WordParser.test("ril7v", 336, 478)

