#!/bin/bash
set -e


# Require settings.json to exist
if [ ! -f settings.json ]; then
  echo "ERROR: settings.json not found. Please copy settings.example.json and edit it with your credentials."
  exit 1
fi

# Remove old Docker image if exists
docker rmi -f elering-visualizer:latest 2>/dev/null || true

# Build Docker image (single-arch by default)
docker build -t elering-visualizer:latest .

# For multi-arch builds, uncomment the following and ensure buildx is set up:
# docker buildx build --platform linux/amd64,linux/arm64 -t elering-visualizer:latest --push .


# Run Docker container with WSGI (Waitress)
# Remove any previous container with the same name
docker rm -f elering-visualizer-run 2>/dev/null || true
docker run -d --name elering-visualizer-run --restart always -p 8889:8889 -v "$PWD/settings.json:/app/settings.json:ro" --env-file "$PWD/.env" elering-visualizer
