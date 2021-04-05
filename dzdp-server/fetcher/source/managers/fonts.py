import os
import re
import sys
import json
import requests
from logging import Logger
from fontTools.ttLib import TTFont

from fetcher.source import utils


class Word:
    def __init__(self, name, x, y):
        self.name = name
        self.x = int(float(x))
        self.y = int(float(y))

    def __str__(self):
        return "name: %s, x: %s, y %s" % (self.name, self.x, self.y)

    def __repr__(self):
        return self.__str__()


class WordParser:
    def __init__(self, logger: Logger):
        self.logger = logger
        self._offset_x = None
        self._offset_y = None

    def parse(self, svg_text, word: Word):

        transfer_tuple_list = self._read_transfer_tuple_list(svg_text)
        transfer_dict = dict(transfer_tuple_list)

        row_key = str(word.y + self._offset_y)
        col_index = (word.x + self._offset_x) // 14

        try:
            return transfer_dict[row_key][col_index]
        except:
            self.logger.error("文字解析失败: %s", word)
            sys.exit()

    def _read_transfer_tuple_list(self, svg_text):
        self._offset_x = 0
        if "#333" in svg_text:
            self._offset_y = 23
        elif "#666" in svg_text:
            self._offset_y = 15
        else:
            self.logger.error("解析规则改变")
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
        return words


class FontManager():
    def __init__(self, logger: Logger):
        self.dir = utils.make_dirs("/fonts")
        self.logger = logger

    def download_shop_fonts(self, r_text):
        try:
            url = "https:" + re.findall(' href="(//s3plus.meituan.net/v1/.*?)">', r_text)[0]
        except:
            with open(self.dir + "/shop_font.html", "w", encoding="utf-8") as fs:
                fs.write(r_text)
            self.logger.warning("save shop_font.html")
            return None

        css_r_text = requests.get(url).text
        font_url_list = re.findall(',url\("(.*?\.woff"\).*?\{)', css_r_text)

        result_dict = {}

        tag_list = ["reviewTag", "address", "tagName", "shopNum"]
        for font_url in font_url_list:
            for tag in tag_list:
                if tag in font_url:
                    tag_url = "https:" + re.findall('(//.*?woff)', font_url)[0]
                    tag_file = self.dir + "/" + tag_url[-13:-5]

                    result_dict[tag] = tag_file

                    if os.path.exists(tag_file):
                        continue
                    r = requests.get(tag_url)
                    with open(tag_file, "wb") as fs:
                        fs.write(r.content)
                    tag_data = TTFont(tag_file)
                    tag_data.saveXML(tag_file)

                    with open(tag_file, 'r', encoding="utf-8") as fs:
                        tag_xml = fs.read()
                    tmp = re.findall('<GlyphOrder>(.*?)</GlyphOrder>', tag_xml, re.S)[0]
                    tmp = re.findall('<GlyphID id=".*?" name="(.*?)"/>', tmp)

                    directory = utils.make_dirs("/assets")
                    with open(directory + "/fonts.json", 'r', encoding="utf-8") as fs:
                        font_dict = json.load(fs)

                    tag_dict = {}

                    for i in range(2, 603):
                        tmp_str = 'glyph' + str(i)
                        tag_dict[tmp[i]] = font_dict[tmp_str]

                    with open(tag_file, 'w', encoding='utf-8') as fs:
                        json.dump(tag_dict, fs, ensure_ascii=False)

        return result_dict

    def download_review_fonts(self, r_text):
        try:
            url = "https:" + re.findall(' href="(//s3plus.meituan.net/v1/.*?)">', r_text)[0]
        except:
            with open(self.dir + "/review_font.html", "w", encoding="utf-8") as fs:
                fs.write(r_text)
            self.logger.warning("save review_font.html")
            return None

        r = requests.get(url)

        with open(self.dir + "/review_font.css", "wb") as fs:
            fs.write(r.content)

        words = WordParser.get_words(r.text)

        type_tuple_list = re.findall('\[class\^="(.*?)"\].*?url\((//s3plus.meituan.net/v1/.*?)\)', r.text, re.S)

        result_dict = {}
        for type_tuple in type_tuple_list:
            (type, type_url) = type_tuple
            type_url = "https:" + type_url
            type_file = self.dir + '/' + type_url[-18:-4]

            result_dict[type] = type_file

            if os.path.exists(type_file):
                continue
            r = requests.get(type_url)
            with open(self.dir + "/svg-" + type + ".xml", "wb") as fs:
                fs.write(r.content)
            parser = WordParser(self.logger)
            word_transfer_dict = {}
            for word in words:
                if type != word.name[:len(type)]:
                    continue
                word_transfer_dict[word.name] = parser.parse(r.text, word)
            with open(type_file, "w", encoding="utf-8") as fs:
                json.dump(word_transfer_dict, fs, ensure_ascii=False)
        return result_dict
