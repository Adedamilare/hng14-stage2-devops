#!/bin/bash

set -e

echo "🚀 Starting deployment..."

# Pull latest images (built in CI)
docker-compose pull

# Start new API container (temporary name)
echo "🆕 Starting new API container..."
docker-compose up -d --no-deps --scale api=2 api

echo "⏳ Waiting for new container to become healthy..."

# Wait up to 60 seconds
timeout 60 bash -c '
until curl -fs http://localhost:8000/health > /dev/null; do
  sleep 2
done
'

# Check result
if [ $? -eq 0 ]; then
  echo "✅ New container is healthy. Scaling down old container..."
  docker-compose up -d --no-deps --scale api=1 api
else
  echo "❌ Health check failed. Rolling back..."
  docker-compose up -d --no-deps --scale api=1 api
  exit 1
fi

echo "🎉 Deployment successful!"