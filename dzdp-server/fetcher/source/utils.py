import os
import json
from types import SimpleNamespace

from fetcher.config import BASE_DIR


# dir should start with "/"
def make_dirs(rel_dir):
    abs_dir = BASE_DIR + rel_dir
    if not os.path.exists(abs_dir):
        os.makedirs(abs_dir)
    return abs_dir


def json2obj(origin):
    return json.loads(json.dumps(origin), object_hook=lambda x: SimpleNamespace(**x))


def dict2str(origin, split="&", kv="="):
    return split.join(["{}{}{}".format(x, kv, y) for x, y in origin.items()])


def get_file(dir_name, filename):
    return make_dirs("/" + dir_name) + filename
