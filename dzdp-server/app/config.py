import os
import app


BASE_DIR = os.path.dirname(app.__file__)


class BaseConfig:
    JSON_AS_ASCII = False
    REDIS_QUEUES = ["default"]
    pass


class DevConfig(BaseConfig):
    DEBUG = True
    REDIS_URL = 'redis://localhost:6379/0'
    pass


class ProdConfig(BaseConfig):
    DEBUG = False
    REDIS_URL = 'redis://redis:6379/0'
    pass


configs = {
    'dev': DevConfig,
    'prod': ProdConfig,
    'default': ProdConfig
}
