#!/bin/bash
set -e


# Generate default settings.json if not present
if [ ! -f settings.json ]; then
  if [ -f settings.example.json ]; then
    echo "settings.json not found. Copying settings.example.json as default."
    cp settings.example.json settings.json
  else
    echo "ERROR: Neither settings.json nor settings.example.json found. Cannot continue."
    exit 1
  fi
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
