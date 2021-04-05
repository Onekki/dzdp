import os

import redis
from flask import request, jsonify, send_from_directory
from rq import Queue, Connection

from app import create_app
from app.source.job_creator import fetch

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

REDIS_URL = app.config["REDIS_URL"]
REDIS_QUEUES = app.config["REDIS_QUEUES"]


@app.route("/")
def index():
    return "Hello World!"


@app.route("/test", methods=["POST", "GET"])
def test():
    resp = {
        "code": 0,
        "msg": "Success",
        "data": {
            "args": request.args,
            "form": request.form,
            "query_string": request.query_string.decode("utf-8"),
            "json": request.json
        }
    }
    return jsonify(resp)


@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    from fetcher.source.utils import make_dirs
    directory = make_dirs("/outputs")
    return send_from_directory(directory, filename, as_attachment=True)


@app.route("/job", methods=["POST"])
def run_fetch():
    try:
        config_dict = request.json
        job_id = config_dict["username"]
        with Connection(redis.from_url(REDIS_URL)):
            queue = Queue(default_timeout=-1)
            job = queue.fetch_job(job_id)
        if not job or (job and job.is_failed):
            job = queue.enqueue(fetch, config_dict, job_id=job_id)
            resp = {
                "code": 0,
                "msg": "Job is created successfully",
                "job": {
                    "id": job.get_id(),
                    "status": job.get_status(),
                    "result": job.result
                }
            }
        else:
            resp = {
                "code": -1,
                "msg": "Job has been exist",
                "job": {
                    "id": job.get_id(),
                    "status": job.get_status(),
                    "result": job.result
                }

            }
    except Exception as e:
        resp = {
            "code": -2,
            "msg": "Job create failed: " + str(e)
        }
    return jsonify(resp)


@app.route("/jobs")
def get_jobs():
    with Connection(redis.from_url(REDIS_URL)):
        queue = Queue(default_timeout=-1)
        jobs = queue.get_jobs()
    if jobs is not None:
        resp = {
            "code": 0,
            "msg": "Success",
            "data": list(map(lambda job: {
                "id": job.get_id(),
                "status": job.get_status(),
                "result": job.result
            }, jobs))
        }
    else:
        resp = {
            "code": -1,
            "msg": "No job created"
        }
    return jsonify(resp)


@app.route("/jobs/<job_id>")
def get_job(job_id):
    with Connection(redis.from_url(REDIS_URL)):
        queue = Queue(default_timeout=-1)
        job = queue.fetch_job(job_id)
    if job:
        if job.result:
            result = job.result
        elif job.is_failed:
            result = job.exc_info.strip().split('\n')[-1].replace("Exception: ", "")
        else:
            result = None
        resp = {
            "code": 0,
            "msg": "Success",
            "data": {
                "id": job.get_id(),
                "status": job.get_status(),
                "result": result
            }
        }
    else:
        resp = {
            "code": -1,
            "msg": "Job not found"
        }
    return jsonify(resp)


if __name__ == "__main__":
    app.run(debug=True)
