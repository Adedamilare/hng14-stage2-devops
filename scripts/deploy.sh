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

# Start new API container
NEW_COUNT=$((CURRENT_COUNT + 1))
echo "🆕 Scaling up to $NEW_COUNT containers..."
$DOCKER_COMPOSE up -d --no-deps --scale api=$NEW_COUNT api

echo "⏳ Waiting for new container to become healthy..."

# Increased timeout to 120 seconds for slow startups
MAX_ATTEMPTS=60
ATTEMPT=1

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
  echo "Health check attempt $ATTEMPT/$MAX_ATTEMPTS..."
  
  # Check container health status
  CONTAINER_ID=$($DOCKER_COMPOSE ps -q api | head -1)
  HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' $CONTAINER_ID 2>/dev/null || echo "starting")
  
  echo "Health status: $HEALTH_STATUS"
  
  if [ "$HEALTH_STATUS" = "healthy" ]; then
    echo "✅ Container is healthy!"
    break
  elif [ "$HEALTH_STATUS" = "unhealthy" ]; then
    echo "❌ Container is unhealthy!"
    $DOCKER_COMPOSE logs --tail=20 api
    break
  fi
  
  # Also try HTTP check as backup
  if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ HTTP health check passed!"
    break
  fi
  
  sleep 2
  ATTEMPT=$((ATTEMPT + 1))
done

if [ $ATTEMPT -le $MAX_ATTEMPTS ] && [ "$HEALTH_STATUS" != "unhealthy" ]; then
  echo "✅ New container is healthy. Scaling down old container..."
  $DOCKER_COMPOSE up -d --no-deps --scale api=1 api
  echo "🧹 Cleaning up old containers..."
  $DOCKER_COMPOSE rm -f
else
  echo "❌ Health check failed after $MAX_ATTEMPTS attempts"
  echo "📋 Full API logs:"
  $DOCKER_COMPOSE logs --tail=50 api
  echo "🔄 Rolling back..."
  $DOCKER_COMPOSE up -d --no-deps --scale api=1 api
  exit 1
fi

echo "🎉 Deployment successful!"
$DOCKER_COMPOSE ps