FROM python:3.11-slim@sha256:<sha256:92c262cbb2e99cdc16218338d74fbe518055c13d224d942708f70f8042ff6d18> AS builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: runtime
FROM python:3.11-slim@sha256:<sha256:92c262cbb2e99cdc16218338d74fbe518055c13d224d942708f70f8042ff6d18>

# Install curl for health check
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update && \ 
    CURL_VERSION="$(apt-cache policy curl | grep 'Candidate:' | awk '{print $2}')" && \
    apt-get install -y --no-install-recommends curl="$CURL_VERSION" && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 10001 appuser

WORKDIR /app

# Copy installed dependencies from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY . .

# Set ownership
RUN chown -R appuser:appuser /app /home/appuser/.local

# Switch to non-root user
USER appuser

# Ensure Python can find the installed packages
ENV PATH=/home/appuser/.local/bin:$PATH

# Expose port
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl --fail http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]