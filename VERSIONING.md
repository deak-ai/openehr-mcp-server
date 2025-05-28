# Versioning Strategy

This document outlines the versioning strategy for the openEHR MCP Server project.

## Semantic Versioning

We follow [Semantic Versioning 2.0.0](https://semver.org/) for version numbering:

```
MAJOR.MINOR.PATCH[-PRERELEASE]
```

- **MAJOR**: Incremented for incompatible API changes
- **MINOR**: Incremented for backward-compatible new functionality
- **PATCH**: Incremented for backward-compatible bug fixes
- **PRERELEASE**: Optional suffix for pre-release versions (e.g., `-beta.1`, `-rc.2`)

## Version Management

### Version File

The canonical source of truth for the current version is the `VERSION` file in the repository root.

### Git Tags

Each release is tagged in Git with a tag name prefixed with `v`:

```
v1.0.0
v1.0.1
v1.1.0-beta.1
```

### Branch Strategy

- **Feature branches**: `feature/#issue-description`
- **Release branches**: `release/x.y.z`
- **Hotfix branches**: `hotfix/x.y.z`

## Docker Images

### Image Tags

Docker images are tagged with several identifiers:

- **Version tag**: `ctodeakai/openehr-mcp-server:1.0.0`
- **Version with commit hash**: `ctodeakai/openehr-mcp-server:1.0.0-a1b2c3d`
- **Major version latest**: `ctodeakai/openehr-mcp-server:1-latest`
- **Latest stable** (optional): `ctodeakai/openehr-mcp-server:latest`

### Docker Hub

Official images are published to Docker Hub under the `ctodeakai` namespace.

## Version Update Process

1. Determine the new version number based on the changes made
2. Run the version update script: `./update_version.sh 1.0.0`
3. Push the new tag to GitHub: `git push origin v1.0.0`
4. Build and push Docker images: `./build.sh --push [--latest]`

## Version Scripts

- **update_version.sh**: Updates the VERSION file and creates a Git tag
- **build.sh**: Builds and tags Docker images based on the current version

Use the `--latest` flag with `build.sh` only when building the most recent stable release.
