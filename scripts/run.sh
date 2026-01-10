#!/bin/bash
set -e

# Resolve script and project root paths so script works when invoked from anywhere
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"


# Remove old Docker image if exists
docker rmi -f elering-visualizer:latest 2>/dev/null || true

# Build Docker image (single-arch by default)
docker build -t elering-visualizer:latest "$PROJECT_ROOT"


# Remove any previous container with the same name
docker rm -f elering-visualizer-run 2>/dev/null || true
MOUNT_SETTINGS=""
if [ -f "$PROJECT_ROOT/settings.json" ]; then
	echo "Mounting host settings.json into container."
	MOUNT_SETTINGS=( -v "$PROJECT_ROOT/settings.json:/app/settings.json:ro" )
fi

# Use host .env if present, otherwise rely on container env or --env-file absence
ENV_FILE_ARG=""
if [ -f "$PROJECT_ROOT/.env" ]; then
	ENV_FILE_ARG=( --env-file "$PROJECT_ROOT/.env" )
fi

docker run -d --name elering-visualizer-run --restart always -p 8889:8889 "${MOUNT_SETTINGS[@]}" "${ENV_FILE_ARG[@]}" elering-visualizer

