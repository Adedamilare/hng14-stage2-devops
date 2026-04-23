from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import redis
import uuid
import os
import logging

app = FastAPI()


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Load environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))


# Initialize Redis (only once)
try:
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=False,
        socket_connect_timeout=5,
        socket_timeout=5,
    )
    # Test connection
    r.ping()
    logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
except Exception as e:
    logger.error(f"Failed to connect to Redis: {e}")
    r = None


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
    """Health check endpoint - returns 200 if healthy, 500 if not"""
    try:
        if r is None:
            logger.error("Redis client not initialized")
            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "error": "Redis not connected"}
            )

        # Test Redis connection
        r.ping()
        return {"status": "ok"}
    except redis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": "Redis connection failed"}
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )


# FIX: Added missing user creation endpoint (api_user_creation_cmd)
@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user():
    user_id = str(uuid.uuid4())
    r.hset(f"user:{user_id}", "status", "active")
    return {"user_id": user_id, "status": "active"}


@app.post("/jobs", status_code=status.HTTP_201_CREATED)
def create_job():
    job_id = str(uuid.uuid4())
    r.lpush("job", job_id)
    r.hset(f"job:{job_id}", "status", "queued")
    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    status_val = r.hget(f"job:{job_id}", "status")
    if not status_val:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job_id,
        "status": status_val.decode(),
    }
