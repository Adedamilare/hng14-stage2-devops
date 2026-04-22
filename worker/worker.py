import logging
import os
import time

import redis


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Load environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
QUEUE_NAME = os.getenv("QUEUE_NAME", "jobs")


# Initialize Redis
r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
)


def process_job(job_id):
    logger.info(f"Processing job {job_id}")
    time.sleep(2)  # simulate work
    r.hset(f"job:{job_id}", "status", "completed")
    logger.info(f"Done: {job_id}")


while True:
    job = r.brpop(QUEUE_NAME, timeout=5)

    if job is None:
        continue

    _, job_id = job  # already string because decode_responses=True

    try:
        process_job(job_id)
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}")
