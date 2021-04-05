import json
import re

from bs4 import BeautifulSoup

from fetcher.source.entities import Config, Shop, Review, Product
from fetcher.source.managers import RequestManager, FontManager, DbManager, LoggerManager

from fetcher.source import utils


class Fetcher:
    def __init__(self, config_dict):
        config: Config = utils.json2obj(config_dict)
        self.logger = LoggerManager(config.city).logger
        self.requestManager = RequestManager(config, self.logger)
        self.fontManager = FontManager(self.logger)
        self.dbManager = DbManager(config.city, config.category_ids, self.logger)

    @staticmethod
    def test_instance():
        directory = utils.make_dirs("/assets")
        with open(directory + "/config.json") as fp:
            config_dict = json.load(fp)
        return Fetcher(config_dict)

    def start(self):
        categories = self.dbManager.query_categories()
        for category in categories:
            self.get_shops(category, category.shop_page_done + 1)
            break

    def get_shops(self, category, page):
        url = "http://www.dianping.com/" + str(category.category_id) + "o11"
        if page != 1:
            url += ("p" + str(page))
        r_text = self.requestManager.request(url).text

        font_file_name_dict = self.fontManager.download_shop_fonts(r_text)
        if font_file_name_dict is not None:
            r_text = RequestManager.transfer_shop_word(r_text, font_file_name_dict)

        soup = BeautifulSoup(r_text, "lxml")

        if category.shop_page == 0:
            category.shop_page = int(soup.select(".page a")[-2].text)
            self.dbManager.update_category(category)

        shop_list = soup.select(".shop-list li")
        for shop_item in shop_list:
            shop = Shop()
            try:
                shop.shop_id = shop_item.select(".pic a")[0]["data-shopid"].strip()
            except:
                pass
            try:
                shop.name = shop_item.select(".tit a")[0].text.replace("\n", "").strip()
            except:
                pass
            try:
                shop.cover = shop_item.select(".pic img")[0]["src"].strip()
            except:
                pass
            try:
                shop.review_number = int(shop_item.select(".comment b")[0].text.strip())
            except:
                pass

            shop_tuple = self.dbManager.query_shop_as_tuple(shop.shop_id)
            # 数据库没有查询到该商店
            if shop_tuple is None:
                self.dbManager.insert_shop(category.category_id, shop)
            else:
                (review_page, review_page_done, product_number, product_number_done) = shop_tuple
                shop.review_page = review_page
                shop.review_page_done = review_page_done
                shop.product_number = product_number
                shop.product_number_done = product_number_done

            if shop.product_number == 0 or shop.product_number_done < shop.product_number:
                # 开始爬取店铺详情
                shop = self.get_products(shop)

            if shop.review_page == 0 or shop.review_page_done < shop.review_page:
                # 开始递归爬评论
                self.get_reviews(shop, shop.review_page_done + 1)

                # 本页面所有店铺爬取完毕
        category.shop_page_done = page
        self.dbManager.update_category(category)

        if page < category.shop_page:
            self.get_shops(category, page + 1)

    def get_products(self, shop: Shop):
        url = "http://www.dianping.com/shop/" + str(shop.shop_id)
        r_text = self.requestManager.request(url).text

        soup = BeautifulSoup(r_text, "lxml")

        try:
            shop.address = soup.select(".address")[0].text.replace("\n", "").strip()
        except:
            pass
        try:
            shop.phone = soup.select(".tel .item")[0].text.strip()
        except:
            pass
        try:
            shop.opening_hours = soup.select(".info-indent .item")[0].text.replace("\n", "").strip()
        except:
            pass
        try:
            breadcrumb_as_list = list(map(lambda x: x.text.replace("\n", "").strip(), soup.select(".breadcrumb a")))
            shop.breadcrumb = json.dumps(breadcrumb_as_list, ensure_ascii=False)
        except:
            pass

        self.dbManager.update_shop(shop)

        try:
            porduct_url_as_list = list(map(lambda x: x["href"], soup.select("#sales .group a")))
            if shop.product_number == 0 or shop.product_number_done < shop.product_number:
                self.get_product(shop, shop.product_number_done, porduct_url_as_list)
        except:
            pass

        return shop

    def get_product(self, shop: Shop, index, porduct_url_list):

        if shop.product_number == 0:
            shop.product_number = len(porduct_url_list)
            self.dbManager.update_shop_product(shop)

        url = porduct_url_list[index]
        r_text = self.requestManager.request_html(url)

        soup = BeautifulSoup(r_text, "lxml")

        product = Product()
        try:
            product.product_id = re.search("productid=(.*?)&shopid", url).group(1)
        except:
            pass
        try:
            product.name = soup.select(".product-name")[0].text.strip()
        except:
            pass
        try:
            product.price = soup.select(".price span")[1].text.strip()
        except:
            pass
        try:
            cover = soup.select(".img-item")[0]["style"]
            product.cover = re.search("url\(\"(.*?)\"\);", cover).group(1)
        except:
            pass
        try:
            good_list = soup.select(".good")
            if len(good_list) > 0:
                goods = []
                for good_item in good_list:
                    good = {}
                    good["good_name"] = good_item.select(".good-name")[0].text.strip()
                    good_attr_list = good_item.select(".good-attr")
                    if len(good_attr_list) > 0:
                        good["good_attrs"] = []
                        for good_attr_item in good_attr_list:
                            good_attr = {}
                            good_attr["good_attr_name"] = good_attr_item.select(".attr-name")[0].text.strip()
                            good_attr["good_attr_value"] = good_attr_item.select(".attr-value")[0].text.strip()
                            good["good_attrs"].append(good_attr)
                    goods.append(good)
                product.detail = json.dumps(goods, ensure_ascii=False)
        except:
            pass
        try:
            product.intro = soup.select(".product-intro img")[0]["src"].strip()
        except:
            pass
        try:
            technician_list = soup.select(".technician")
            if len(technician_list) > 0:
                technicians = []
                for technician_item in technician_list:
                    tech_photo = technician_item.select(".tech-photo")[0]["style"]
                    tech_photo = re.search("url\(\"(.*?)\"\);", tech_photo).group(1)
                    tech_name = technician_item.select(".tech-name")[0].text.strip()
                    tech_title = technician_item.select(".tech-title")[0].text.strip()
                    tech_work_year = technician_item.select(".tech-work-year")[0].text.strip()
                    tech_tag = technician_item.select(".tech-tag")[0].text.strip()
                    technicians.append({
                        "tech_photo": tech_photo,
                        "tech_name": tech_name,
                        "tech_title": tech_title,
                        "tech_work_year": tech_work_year,
                        "tech_tag": tech_tag
                    })
                product.technicians = json.dumps(technicians, ensure_ascii=False)
        except:
            pass

        self.dbManager.insert_product(shop.shop_id, product)

        shop.product_number_done = index + 1
        self.dbManager.update_shop_product(shop)

        if shop.product_number_done < shop.product_number:
            self.get_product(shop, shop.product_number_done, porduct_url_list)

    def get_reviews(self, shop: Shop, page):
        url = "http://www.dianping.com/shop/" + str(shop.shop_id) + "/review_all"
        if page != 1:
            url += ("/p" + str(page))
        r_text = self.requestManager.request(url).text

        font_file_name_dict = self.fontManager.download_review_fonts(r_text)
        if font_file_name_dict is not None:
            r_text = RequestManager.transfer_review_word(r_text, font_file_name_dict)

        soup = BeautifulSoup(r_text, "lxml")

        if shop.review_page == 0:
            shop.review_page = int(soup.select(".reviews-pages a")[-2]["data-pg"])
            self.dbManager.update_shop_review(shop)

        review_list = soup.select(".reviews-items > ul > li")
        for review_item in review_list:
            review = Review()
            try:
                review.review_id = review_item.select('.actions a')[0]['data-id'].strip()
            except:
                pass
            try:
                review.user_name = review_item.select(".name")[0].text.strip()
            except:
                pass
            try:
                review.avatar = review_item.select("img")[0]["data-lazyload"].strip()
            except:
                pass
            try:
                review.content = review_item.select('.review-words')[0].text.replace("\n", "").replace("\r",
                                                                                                       "").replace(
                    "收起评价", "").strip()
            except:
                pass
            try:
                review.score_kw = review_item.select(".score .item")[0].text.strip()
                review.score_hj = review_item.select(".score .item")[1].text.strip()
                review.score_fw = review_item.select(".score .item")[2].text.strip()
            except:
                pass
            self.dbManager.insert_review(shop.shop_id, review)

        # 本页面所有评论爬取完毕
        shop.review_page_done = page
        self.dbManager.update_shop_review(shop)

        if page < shop.review_page:
            self.get_reviews(shop, page + 1)
