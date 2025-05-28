#!/bin/bash
set -e

# Check if a new version is provided
if [ $# -ne 1 ]; then
  echo "Usage: $0 <new_version>"
  echo "Example: $0 1.0.0"
  exit 1
fi

NEW_VERSION=$1

# Validate semantic versioning format
if ! [[ $NEW_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9\.]+)?$ ]]; then
  echo "Error: Version must follow semantic versioning format (MAJOR.MINOR.PATCH[-PRERELEASE])"
  exit 1
fi

# Get the current version
CURRENT_VERSION=$(cat VERSION)

echo "Updating version from $CURRENT_VERSION to $NEW_VERSION"

# Update the VERSION file
echo $NEW_VERSION > VERSION

# Create a git tag
echo "Creating git tag v$NEW_VERSION"
git add VERSION
git commit -m "Bump version to $NEW_VERSION"
git tag -a "v$NEW_VERSION" -m "Version $NEW_VERSION"

echo "Version updated successfully"
echo "To push the tag to the remote repository, run: git push origin v$NEW_VERSION"
echo "To build a Docker image with this version, run: ./build.sh"
