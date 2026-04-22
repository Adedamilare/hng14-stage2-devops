from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis
import uuid
import os


app = FastAPI()

# Load environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Initialize Redis (only once)
r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=False,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/jobs")
def create_job():
    job_id = str(uuid.uuid4())
    r.lpush("job", job_id)
    r.hset(f"job:{job_id}", "status", "queued")
    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    status = r.hget(f"job:{job_id}", "status")

    if not status:
        return {"error": "not found"}

    return {
        "job_id": job_id,
        "status": status.decode(),
    }
