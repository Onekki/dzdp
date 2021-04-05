from flask import Flask

from app.config import configs


def create_app(config_name):
    flask_app = Flask(__name__)
    flask_app.config.from_object(configs[config_name])
    return flask_app
