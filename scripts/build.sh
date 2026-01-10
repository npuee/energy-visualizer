#!/bin/bash
set -euo pipefail

# Build multi-architecture Docker image (amd64 and arm64)
# Requires Docker Buildx (Docker 19.03+)
# Usage: ./scripts/build.sh [--push] [image:tag]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

IMAGE_NAME=${1:-elering-visualizer}
TAG=${2:-latest}
PUSH=false
if [ "$IMAGE_NAME" = "--push" ]; then
  PUSH=true
  IMAGE_NAME=${2:-elering-visualizer}
  TAG=${3:-latest}
fi
if [ "${1:-}" = "--push" ]; then
  PUSH=true
  IMAGE_NAME=${2:-elering-visualizer}
  TAG=${3:-latest}
fi

FULL_IMAGE="$IMAGE_NAME:$TAG"

echo "Project root: $PROJECT_ROOT"
echo "Building multi-arch image: $FULL_IMAGE (push=$PUSH)"

# Create builder if not exists
if ! docker buildx inspect multiarch-builder >/dev/null 2>&1; then
  docker buildx create --name multiarch-builder --use
fi

docker buildx use multiarch-builder

BUILD_CMD=(docker buildx build --platform linux/amd64,linux/arm64 -t "$FULL_IMAGE")

if [ "$PUSH" = true ]; then
  BUILD_CMD+=(--push)
else
  # --load only supports the current platform; for multi-arch images prefer --push
  BUILD_CMD+=(--load)
fi

# Set context to project root (so Dockerfile and app/ are found)
BUILD_CMD+=("$PROJECT_ROOT")

"${BUILD_CMD[@]}"

if [ "$PUSH" = true ]; then
  echo "Multi-arch image pushed as $FULL_IMAGE for amd64 and arm64."
else
  echo "Multi-arch build finished (note: --load may only load the current platform). Built as $FULL_IMAGE." 
fi
