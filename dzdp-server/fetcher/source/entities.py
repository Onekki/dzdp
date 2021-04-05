# 实体

class Config:
    def __init__(self):
        self.username = None
        self.email = None
        self.phone = None
        self.city = None
        self.category_ids = None
        self.headers = None


class Category:
    def __init__(self):
        self.category_id = None

        self.shop_page = 0
        self.shop_page_done = 0


class Shop:
    def __init__(self):
        self.shop_id = None
        self.name = None
        self.cover = None
        self.address = None
        self.phone = None
        self.opening_hours = None
        self.breadcrumb = None
        self.review_number = 0

        self.review_page = 0
        self.review_page_done = 0

        self.product_number = 0
        self.product_number_done = 0


class Review:
    def __init__(self):
        self.review_id = None
        self.nickname = None
        self.avatar = None
        self.content = None
        self.score_star = None
        self.score_kw = None
        self.score_hj = None
        self.score_fw = None
        self.publish_time = None
        self.project = None
        self.technician = None
        self.like_number = None
        self.reply_number = None
        self.collect_number = None
        self.pictures = None


class Product():
    def __init__(self):
        self.product_id = None
        self.name = None
        self.price = None
        self.cover = None
        self.detail = None
        self.intro = None
        self.technicians = None
