FROM python:3.11-slim AS builder

WORKDIR /app

#Install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

#Stage 2: runtime
FROM python:3.11-slim

#Create non-root user
RUN useradd -m appuser

WORKDIR /app

#Copy installed dependencies from builder stage
COPY --from=builder /root/.local /home/appuser/.local

#Copy application code
COPY . .

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Ensure Python can find the installed packages
ENV PATH=/home/appuser/.local/bin:$PATH

#Expose port
EXPOSE 8000

HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]