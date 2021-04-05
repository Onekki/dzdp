import redis
from rq import Connection, Worker

from app.main import app


REDIS_URL = app.config["REDIS_URL"]
REDIS_QUEUES = app.config["REDIS_QUEUES"]


def start_worker():
    redis_connection = redis.from_url(REDIS_URL)
    with Connection(redis_connection):
        worker = Worker(REDIS_QUEUES)
        worker.work()


if __name__ == '__main__':
    start_worker()