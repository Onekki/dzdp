from fetcher.source.fetcher import Fetcher

if __name__ == '__main__':
    fetcher = Fetcher.test_instance()
    fetcher.start()
