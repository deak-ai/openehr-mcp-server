#!/bin/bash
set -e

# Get the version from the VERSION file
VERSION=$(cat VERSION)

# Get the git commit hash
GIT_COMMIT=$(git rev-parse --short HEAD)

# Set the Docker image name
IMAGE_NAME="ctodeakai/openehr-mcp-server"

# Parse command line arguments
PUSH_TO_DOCKERHUB=false
LATEST_TAG=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --push)
      PUSH_TO_DOCKERHUB=true
      shift
      ;;
    --latest)
      LATEST_TAG=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "Building Docker image for version $VERSION (commit $GIT_COMMIT)"

# Build the Docker image with version tag
docker build -t "$IMAGE_NAME:$VERSION" .

# Add git commit tag
docker tag "$IMAGE_NAME:$VERSION" "$IMAGE_NAME:$VERSION-$GIT_COMMIT"

# Add major version tag (e.g., 1-latest)
MAJOR_VERSION=$(echo $VERSION | cut -d. -f1)
docker tag "$IMAGE_NAME:$VERSION" "$IMAGE_NAME:$MAJOR_VERSION-latest"

# Add latest tag if requested
if [ "$LATEST_TAG" = true ]; then
  echo "Tagging as latest"
  docker tag "$IMAGE_NAME:$VERSION" "$IMAGE_NAME:latest"
fi

# Push to Docker Hub if requested
if [ "$PUSH_TO_DOCKERHUB" = true ]; then
  echo "Pushing to Docker Hub"
  docker push "$IMAGE_NAME:$VERSION"
  docker push "$IMAGE_NAME:$VERSION-$GIT_COMMIT"
  docker push "$IMAGE_NAME:$MAJOR_VERSION-latest"
  
  if [ "$LATEST_TAG" = true ]; then
    docker push "$IMAGE_NAME:latest"
  fi
fi

echo "Build completed successfully"
echo "Image: $IMAGE_NAME:$VERSION"
