import os
import fetcher


BASE_DIR = os.path.dirname(fetcher.__file__)


class BaseConfig:
    JSON_AS_ASCII = False
    pass


class DevConfig(BaseConfig):
    DEBUG = True
    pass


class ProdConfig(BaseConfig):
    DEBUG = False
    pass


configs = {
    'dev': DevConfig,
    'prod': ProdConfig,
    'default': DevConfig
}
