### api/main.py (Line 8)

Issue:
Hardcoded Redis URL using localhost

Impact:
Fails in containerized environment

Fix:
Replaced with environment variable

Issue:
No /health endpoint for Docker HEALTHCHECK

Fix: Add GET /health that pings Redis

---

### worker/worker.py (Line 6)

Issue: 
redis.Redis(host="localhost") — same hardcoded host bug

Fix: Use REDIS_HOST env var

Issue:
Busy loop consuming CPU

Impact:
High CPU usage in production

Fix:
Replaced with blocking Redis call (BLPOP)