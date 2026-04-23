#!/bin/bash

set -e

echo "🚀 Starting deployment..."

DOCKER_COMPOSE="docker compose"

# Pull latest images
echo "📦 Pulling latest images..."
$DOCKER_COMPOSE pull

# Get current container count
CURRENT_COUNT=$($DOCKER_COMPOSE ps -q api | wc -l)
echo "Current API containers: $CURRENT_COUNT"

# Start new API container (scale to current + 1)
NEW_COUNT=$((CURRENT_COUNT + 1))
echo "🆕 Scaling up to $NEW_COUNT containers..."
$DOCKER_COMPOSE up -d --no-deps --scale api=$NEW_COUNT api

echo "⏳ Waiting for new container to become healthy..."

# Wait for health check
timeout 60 bash -c '
while true; do
  if curl -fs http://localhost:8000/health | grep -q "\"status\":\"ok\""; then
    echo "✅ Health check passed"
    break
  fi
  echo "Waiting for health check..."
  sleep 2
done
'

if [ $? -eq 0 ]; then
  echo "✅ New container is healthy. Scaling back to 1 container..."
  $DOCKER_COMPOSE up -d --no-deps --scale api=1 api
  
  echo "🧹 Cleaning up old containers..."
  $DOCKER_COMPOSE rm -f
else
  echo "❌ Health check failed. Rolling back to 1 container..."
  $DOCKER_COMPOSE up -d --no-deps --scale api=1 api
  exit 1
fi

echo "🎉 Deployment successful!"
$DOCKER_COMPOSE ps