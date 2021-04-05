import sqlite3
from logging import Logger

from fetcher.source import utils
from fetcher.source.entities import Category, Shop, Review, Product


class DbManager:
    def __init__(self, db_name, category_ids, logger: Logger):
        directory = utils.make_dirs("/outputs")
        db_file = directory + "/" + db_name + ".db"

        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS category(
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                category_id TEXT NOT NULL UNIQUE,

                shop_page INTEGER NOT NULL DEFAULT 0,
                shop_page_done INTEGER NOT NULL DEFAULT 0
            );
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS shop(
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                shop_id TEXT NOT NULL UNIQUE,
                name TEXT,
                cover TEXT,
                address TEXT,
                phone TEXT,
                opening_hours TEXT,
                breadcrumb TEXT,
                review_number INTEGER NOT NULL DEFAULT 0,

                review_page INTEGER NOT NULL DEFAULT 0,
                review_page_done INTEGER NOT NULL DEFAULT 0,

                product_number INTEGER NOT NULL DEFAULT 0,
                product_number_done INTEGER NOT NULL DEFAULT 0,

                category_id TEXT
            );
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS review(
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                review_id TEXT NOT NULL UNIQUE,
                nickname TEXT,
                avatar TEXT,
                content TEXT,
                score_star TEXT,
                score_text TEXT,
                publish_time TEXT,
                project TEXT,
                technician TEXT,
                like_number TEXT,
                reply_number TEXT,
                collect_number TEXT,
                pictures TEXT,

                shop_id TEXT
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS product(
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                product_id TEXT NOT NULL UNIQUE,
                name TEXT,
                price TEXT,
                cover TEXT,
                detail TEXT,
                intro TEXT,
                technicians TEXT,

                shop_id TEXT
            );
        """)

        self.logger = logger

        for category_id in category_ids:
            category = Category()
            category.category_id = category_id
            self.insert_category(category)

    def insert_category(self, category: Category):
        try:
            self.cursor.execute("""
                INSERT INTO category (category_id) VALUES(?)
            """, [category.category_id])
            self.conn.commit()
            return True
        except Exception as e:
            self.logger.warning("insert_category %s %s", category.category_id, e)
            return False

    def query_categories(self):
        try:
            self.cursor.execute("""
                SELECT * FROM category WHERE (shop_page = 0) OR (shop_page_done < shop_page AND shop_page != 0)
            """)
            categories = []
            for row in self.cursor:
                category = Category()
                category.id = row[0]
                category.category_id = row[1]
                category.shop_page = row[2]
                categories.append(category)
            return categories
        except Exception as e:
            self.logger.warning("query_categories %s", e)
            return []

    def update_category(self, category: Category):
        try:
            self.cursor.execute("""
                UPDATE category SET shop_page = ?, shop_page_done = ? WHERE category_id = ?
            """, [category.shop_page, category.shop_page_done, category.category_id])
            self.conn.commit()
            return True
        except Exception as e:
            self.logger.warning("update_category %s %s", category.category_id, e)
            return False

    def insert_shop(self, category_id, shop: Shop):
        try:
            self.cursor.execute("""
                INSERT INTO shop (
                    shop_id,
                    name,
                    cover,
                    review_number,
                    category_id
                ) VALUES(?,?,?,?,?)
            """, [
                shop.shop_id,
                shop.name,
                shop.cover,
                shop.review_number,
                category_id
            ])
            self.conn.commit()
            return True
        except Exception as e:
            self.logger.warning("insert_shop %s %s", shop.shop_id, e)
            return False

    def query_shop_as_tuple(self, shop_id):
        try:
            self.cursor.execute("""
                SELECT
                    review_page,
                    review_page_done,
                    product_number,
                    product_number_done
                FROM shop 
                WHERE 
                    shop_id = ?
            """, [shop_id])
            return self.cursor.fetchone()
        except Exception as e:
            self.logger.warning("query_shop_as_tuple %s %s", shop_id, e)
            return None

    def update_shop(self, shop: Shop):
        try:
            self.cursor.execute("""
                UPDATE shop SET
                    address = ?,
                    phone = ?,
                    opening_hours = ?,
                    breadcrumb = ?
                WHERE
                    shop_id = ?
            """, [
                shop.address,
                shop.phone,
                shop.opening_hours,
                shop.breadcrumb,
                shop.shop_id
            ])
            self.conn.commit()
            return True
        except Exception as e:
            self.logger.warning("update_shop %s %s", shop.shop_id, e)
            return False

    def update_shop_product(self, shop: Shop):
        try:
            self.cursor.execute("""
                UPDATE shop SET
                    product_number = ?, 
                    product_number_done = ?
                WHERE 
                    shop_id = ?
            """, [
                shop.product_number,
                shop.product_number_done,
                shop.shop_id
            ])
            self.conn.commit()
            return True
        except Exception as e:
            self.logger.warning("update_shop_product %s %s", shop.shop_id, e)
            return False

    def update_shop_review(self, shop: Shop):
        try:
            self.cursor.execute("""
                UPDATE shop SET
                    review_page = ?, 
                    review_page_done = ?
                WHERE 
                    shop_id = ?
            """, [
                shop.review_page,
                shop.review_page_done,
                shop.shop_id
            ])
            self.conn.commit()
            return True
        except Exception as e:
            self.logger.warning("update_shop_review %s %s", shop.shop_id, e)
            return False

    def insert_review(self, shop_id, review: Review):
        try:
            score_text = "%s%s%s" % (review.score_kw, review.score_hj, review.score_fw)
            self.cursor.execute("""
                INSERT INTO review (
                    review_id, 
                    nickname, 
                    avatar, 
                    content, 
                    score_star,
                    score_text,
                    publish_time,
                    project,
                    technician,
                    like_number,
                    reply_number,
                    collect_number,
                    pictures,
                    shop_id
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, [
                review.review_id,
                review.user_name,
                review.avatar,
                review.content,
                review.score_star,
                score_text,
                review.publish_time,
                review.project,
                review.technician,
                review.like_number,
                review.reply_number,
                review.collect_number,
                review.pictures,
                shop_id
            ])
            self.conn.commit()
        except Exception as e:
            self.logger.warning("insert_review %s %s", review.review_id, e)
            return False

    def insert_product(self, shop_id, product: Product):
        try:
            self.cursor.execute("""
                INSERT INTO product (
                    product_id,
                    name,
                    price,
                    cover,
                    detail,
                    intro,
                    technicians,
                    shop_id
                ) VALUES (?,?,?,?,?, ?,?,?)
            """, [
                product.product_id,
                product.name,
                product.price,
                product.cover,
                product.detail,
                product.intro,
                product.technicians,
                shop_id
            ])
            self.conn.commit()
            return True
        except Exception as e:
            self.logger.warning("insert_product %s %s", product.product_id, e)
            return False

    def __del__(self):
        self.conn.close()