#!/bin/bash

set -e

echo "🚀 Starting deployment..."

DOCKER_COMPOSE="docker compose"

# Pull latest images
echo "📦 Pulling latest images..."
$DOCKER_COMPOSE pull

# Start new API container
echo "🆕 Starting new API container..."
$DOCKER_COMPOSE up -d --no-deps --scale api=2 api

echo "⏳ Waiting for new container to become healthy..."

# Function to check health
check_health() {
  local max_attempts=30
  local attempt=1
  
  while [ $attempt -le $max_attempts ]; do
    echo "Health check attempt $attempt/$max_attempts..."
    
    # Get health response
    response=$(curl -s http://localhost:8000/health)
    http_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
    
    echo "HTTP Status: $http_code"
    echo "Response: $response"
    
    # Check if response contains "status":"ok"
    if echo "$response" | grep -q '"status":"ok"'; then
      echo "✅ Health check passed!"
      return 0
    fi
    
    # Check if it's unhealthy but service is running
    if [ "$http_code" = "503" ]; then
      echo "⚠️  Service is unhealthy (Redis connection issue?)"
    elif [ "$http_code" = "500" ]; then
      echo "⚠️  Service internal error"
    fi
    
    sleep 2
    attempt=$((attempt + 1))
  done
  
  echo "❌ Health check failed after $max_attempts attempts"
  return 1
}

# Run health check with timeout
if check_health; then
  echo "✅ New container is healthy. Scaling down old container..."
  $DOCKER_COMPOSE up -d --no-deps --scale api=1 api
  
  echo "🧹 Cleaning up old containers..."
  $DOCKER_COMPOSE rm -f
else
  echo "❌ Health check failed. Rolling back..."
  $DOCKER_COMPOSE up -d --no-deps --scale api=1 api
  exit 1
fi

echo "🎉 Deployment successful!"

# Show running containers
echo "📋 Current running containers:"
$DOCKER_COMPOSE ps