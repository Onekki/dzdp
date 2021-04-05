from fetcher.source.fetcher import Fetcher
from fetcher.source.managers.notification import FetcherException


def fetch(config_dict):
    f = Fetcher(config_dict)
    f.start()
    return "Job has been finished"
