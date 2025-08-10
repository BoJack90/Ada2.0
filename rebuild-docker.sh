#!/bin/bash
# Script to rebuild Docker containers after adding new dependencies

echo "Stopping running containers..."
docker-compose down

echo "Rebuilding containers with new dependencies..."
docker-compose build --no-cache

echo "Starting containers..."
docker-compose up -d

echo "Docker rebuild complete!"
echo "You can check the logs with: docker-compose logs -f"