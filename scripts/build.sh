#!/bin/bash
set -euo pipefail

# Build multi-architecture Docker image (amd64 and arm64)
# Requires Docker Buildx (Docker 19.03+)
# Usage: ./scripts/build.sh [--push] [image:tag]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

IMAGE_NAME=${1:-docker.io/legal2k/elering-visualizer}
TAG=${2:-latest}
PUSH=false
if [ "$IMAGE_NAME" = "--push" ]; then
  PUSH=true
  IMAGE_NAME=${2:-docker.io/legal2k/elering-visualizer}
  TAG=${3:-latest}
fi
if [ "${1:-}" = "--push" ]; then
  PUSH=true
  IMAGE_NAME=${2:-docker.io/legal2k/elering-visualizer}
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

if [ "$PUSH" = true ]; then
  # Use buildx for multi-arch builds and push to registry
  BUILD_CMD=(docker buildx build --platform linux/amd64,linux/arm64 -t "$FULL_IMAGE" --push "$PROJECT_ROOT")
  "${BUILD_CMD[@]}"
else
  # For local builds: build each arch into temporary tags, assemble a
  # local manifest named without architecture suffixes, then remove the
  # temporary tags so the final manifest is referenced as "$FULL_IMAGE".
  TMP_AMD_TAG="$IMAGE_NAME:tmp-$TAG-amd64"
  TMP_ARM_TAG="$IMAGE_NAME:tmp-$TAG-arm64"

  # Build amd64 into temporary tag
  docker buildx build --platform linux/amd64 -t "$TMP_AMD_TAG" --load "$PROJECT_ROOT"

  # Build arm64 into temporary tag
  docker buildx build --platform linux/arm64 -t "$TMP_ARM_TAG" --load "$PROJECT_ROOT"

  # Try using buildx imagetools to assemble a multi-arch image from the
  # locally-built images. This avoids pulling/pushing to a registry.
  if docker buildx imagetools create --help >/dev/null 2>&1; then
    docker buildx imagetools create -t "$FULL_IMAGE" "$TMP_AMD_TAG" "$TMP_ARM_TAG" || true
    echo "Created multi-arch image $FULL_IMAGE using buildx imagetools."

    # Remove temporary tags to avoid leaving per-arch tags locally
    docker image rm "$TMP_AMD_TAG" || true
    docker image rm "$TMP_ARM_TAG" || true
  else
    # Fallback to docker manifest command if imagetools isn't available
    if docker manifest --help >/dev/null 2>&1; then
      docker manifest create "$FULL_IMAGE" "$TMP_AMD_TAG" "$TMP_ARM_TAG" || true
      docker manifest annotate "$FULL_IMAGE" "$TMP_AMD_TAG" --os linux --arch amd64 || true
      docker manifest annotate "$FULL_IMAGE" "$TMP_ARM_TAG" --os linux --arch arm64 || true
      echo "Created local manifest $FULL_IMAGE referencing amd64 and arm64 images."

      # Do NOT remove temporary tags here because removing them may delete
      # the underlying image objects that the manifest references on some
      # Docker setups; leave them so the manifest entries remain resolvable.
      echo "Left temporary tags: $TMP_AMD_TAG, $TMP_ARM_TAG"
    else
      echo "Neither buildx imagetools nor docker manifest available; built platform-specific images:" 
      echo "  $TMP_AMD_TAG"
      echo "  $TMP_ARM_TAG"
      echo "You can push these to a registry and create a manifest there to assemble a multi-arch image named $FULL_IMAGE."
    fi
  fi
fi

if [ "$PUSH" = true ]; then
  echo "Multi-arch image pushed as $FULL_IMAGE for amd64 and arm64."
else
  echo "Multi-arch build finished (note: --load may only load the current platform). Built as $FULL_IMAGE." 
fi
