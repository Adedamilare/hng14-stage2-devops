import redis
import time
import os
import signal

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
QUEUE_NAME = os.getenv("QUEUE_NAME", "jobs")

r = redis.Redis(host="REDIS_HOST", port="REDIS_PORT", decode_responses=True)

def process_job(job_id):
    print(f"Processing job {job_id}")
    time.sleep(2)  # simulate work
    r.hset(f"job:{job_id}", "status", "completed")
    print(f"Done: {job_id}")

import time

while True:
    job = r.brpop("job", timeout=5)

    if job is None:
        continue

    _, job_id = job
    job_id = job_id.decode("utf-8")

    try:
        process_job(job_id)
    except Exception as e:
        print(f"Error processing job {job_id}: {e}")

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)