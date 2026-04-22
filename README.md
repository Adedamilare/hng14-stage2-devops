# hng14-stage2-devops
# Job Processing System — Production-Ready DevOps Implementation
Overview
This project demonstrates how to take a multi-service application from a flawed, development-ready state to a production-grade system using modern DevOps practices.
The system simulates a job processing pipeline where users submit jobs via a frontend, the API queues them, and a worker processes them asynchronously using Redis.
Beyond functionality, this project emphasizes:
•	Reliability
•	Observability
•	Security
•	Deployment safety
•	Reproducibility

Architecture
Frontend (Node.js)
        │
        ▼
API (FastAPI) ───── Redis
        │
        ▼
     Worker (Python)
Components
Service	Description
Frontend	User interface for submitting and tracking jobs
API	Handles job creation and status retrieval
Worker	Processes jobs from the queue
Redis	Message broker shared between API and worker
________________________________________
Key Features
•	Full containerization using Docker (multi-stage builds)
•	No hardcoded secrets — environment-based configuration
•	Non-root containers for security
•	Health checks for all services
•	Service dependency management using health status (not just startup order)
•	CI/CD pipeline with GitHub Actions
•	Security scanning with Trivy
•	Unit + integration testing
•	Rolling deployment with rollback protection
Project Structure
.
├── api/
├── frontend/
├── worker/
├── docker-compose.yml
├── .env.example
├── README.md
├── FIXES.md
└── .github/workflows/ci.yml

Environment Configuration
All configuration is handled through environment variables.
Step 1: Create your .env file
cp .env.example .env
Step 2: Update values if needed
Example:
REDIS_URL=redis://redis:6379
API_URL=http://api:8000

Running the Application
All commands must be executed from the project root.
Build and start all services
docker compose up --build
Access services
Service	URL
Frontend	http://localhost:3000

API	http://localhost:8000


Running Tests
API Unit Tests
cd api
pytest --cov=app

Linting
flake8 .
eslint frontend/
hadolint api/Dockerfile

Containerization Details
Each service:
•	Uses multi-stage builds
•	Runs as a non-root user
•	Includes a HEALTHCHECK
•	Excludes secrets and unnecessary files

Docker Compose Highlights
•	Internal network for service communication
•	Redis is not exposed to host
•	Services start only when dependencies are healthy
•	CPU and memory limits defined
•	All configuration injected via environment variables

CI/CD Pipeline
Implemented using GitHub Actions.
Pipeline Stages (Strict Order)
1.	Lint
o	flake8 (Python)
o	eslint (JavaScript)
o	hadolint (Dockerfiles)
2.	Test
o	pytest with coverage
o	Coverage report uploaded as artifact
3.	Build
o	Docker images built and tagged (SHA + latest)
o	Images pushed to local registry
4.	Security Scan
o	Trivy scan
o	Pipeline fails on CRITICAL vulnerabilities
5.	Integration Test
o	Full stack launched inside runner
o	Job submitted via frontend
o	Status verified
o	Environment cleaned up
6.	Deploy
o	Runs on main branch only
o	Rolling update strategy:
	New container must pass health check
	Old container remains until success confirmed
	Automatic rollback on failure

Deployment Strategy
•	Zero-downtime deployment approach
•	Health-check-driven promotion
•	Automatic rollback if new version fails within 60 seconds

Bug Fix Documentation
All identified issues and fixes are documented in:
FIXES.md
Each entry includes:
•	File name
•	Line number
•	Description of the issue
•	Exact fix applied

Security Practices
•	No secrets in repository or images
•	.env is ignored via .gitignore
•	Dependency scanning enforced
•	Minimal base images used

Prerequisites
Ensure you have installed:
•	Docker
•	Docker Compose
•	Git

Expected Outcome
After running the system:
•	Frontend loads successfully
•	Jobs can be submitted
•	Worker processes jobs asynchronously
•	Status updates are reflected correctly

 Notes
•	This project is designed to simulate real-world DevOps responsibilities:
o	Debugging broken systems
o	Hardening applications for production
o	Building reliable pipelines
o	Ensuring safe deployments

