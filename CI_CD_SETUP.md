# CI/CD Pipeline Setup Guide

This guide explains how to set up automated Docker image building and deployment to Docker Hub using GitHub Actions.

## 🚀 Overview

The CI/CD pipeline automatically:
- **Builds Docker images** on every commit to main/develop branches
- **Increments version numbers** automatically using semantic versioning
- **Pushes images to Docker Hub** with proper tags
- **Creates GitHub releases** with release notes
- **Supports multi-platform builds** (linux/amd64, linux/arm64)
- **Provides manual triggers** for custom builds

## 📋 Prerequisites

### 1. GitHub Repository Setup
- Repository: `https://github.com/deepak-gunasekaran/apigee-deployment-manager`
- Branch protection rules (optional but recommended)
- Actions enabled

### 2. Docker Hub Account
- Username: `deepakdpk6`
- Repository: `deepakdpk6/apigee-deployment-manager`
- Access token for GitHub Actions

## 🔧 Setup Instructions

### Step 1: Create Docker Hub Access Token

1. **Login to Docker Hub**: https://hub.docker.com
2. **Go to Account Settings** → **Security**
3. **Create New Access Token**:
   - Token Name: `github-actions-apigee-manager`
   - Permissions: `Read, Write, Delete`
4. **Copy the token** (you won't see it again!)

### Step 2: Configure GitHub Secrets

1. **Go to your GitHub repository**
2. **Navigate to**: Settings → Secrets and variables → Actions
3. **Add Repository Secret**:
   - Name: `DOCKER_HUB_TOKEN`
   - Value: `[paste your Docker Hub access token]`

### Step 3: Verify Workflow Files

Ensure these files exist in your repository:

```
.github/
└── workflows/
    ├── docker-build-push.yml    # Main CI/CD pipeline
    └── manual-build.yml         # Manual trigger workflow
```

### Step 4: Test the Pipeline

#### Option A: Automatic Trigger (Recommended)
```bash
# Make a change and push to main branch
echo "# Test change" >> README.md
git add README.md
git commit -m "test: trigger CI/CD pipeline"
git push origin main
```

#### Option B: Manual Trigger
1. Go to **Actions** tab in GitHub
2. Select **Manual Docker Build** workflow
3. Click **Run workflow**
4. Choose version increment type
5. Click **Run workflow**

## 🔄 Versioning Strategy

### Automatic Versioning (Main Branch)
- **Patch increment**: `v1.0.0` → `v1.0.1`
- **Triggered by**: Every push to `main` branch
- **Docker tags**: `v1.0.1`, `latest`

### Branch-based Versioning
- **Main branch**: `v1.0.1`, `latest`
- **Develop branch**: `develop-20240428.123456-abc12345`, `develop`
- **Feature branches**: `feature-branch-abc12345`
- **Pull requests**: `pr-123-abc12345`

### Manual Versioning
- **Patch**: `v1.0.0` → `v1.0.1`
- **Minor**: `v1.0.0` → `v1.1.0`
- **Major**: `v1.0.0` → `v2.0.0`
- **Custom**: Any version you specify

## 🛠️ Local Development Tools

### Version Management Script
```bash
# Show current version info
./scripts/version.sh current

# Increment patch version (1.0.0 → 1.0.1)
./scripts/version.sh patch

# Increment minor version (1.0.0 → 1.1.0)
./scripts/version.sh minor

# Increment major version (1.0.0 → 2.0.0)
./scripts/version.sh major

# Build Docker image locally
./scripts/version.sh build
```

### Manual Docker Build
```bash
# Build with version metadata
docker build \
  --build-arg BUILD_DATE="$(date -u +'%Y%m%d')" \
  --build-arg BUILD_VERSION="v1.0.1" \
  --build-arg COMMIT_SHA="$(git rev-parse --short HEAD)" \
  -t deepakdpk6/apigee-deployment-manager:v1.0.1 \
  .
```

## 📊 Pipeline Workflows

### 1. Main CI/CD Pipeline (`docker-build-push.yml`)

**Triggers**:
- Push to `main` branch → Auto-increment patch version
- Push to `develop` branch → Development build
- Pull requests → PR build (no push to Docker Hub)
- GitHub releases → Release build

**Features**:
- ✅ Automatic semantic versioning
- ✅ Multi-platform builds (amd64, arm64)
- ✅ Docker Hub push with multiple tags
- ✅ GitHub release creation
- ✅ Build caching for faster builds
- ✅ Docker Hub description update

### 2. Manual Build Pipeline (`manual-build.yml`)

**Triggers**:
- Manual workflow dispatch from GitHub Actions UI

**Features**:
- ✅ Choose version increment type (patch/minor/major/custom)
- ✅ Optional Docker Hub push
- ✅ Custom version specification
- ✅ Build-only mode for testing

## 🏷️ Docker Tags Strategy

| Branch/Trigger | Tags Created | Example |
|----------------|--------------|---------|
| **Main branch** | `vX.Y.Z`, `latest` | `v1.0.1`, `latest` |
| **Develop branch** | `develop-YYYYMMDD.HHMMSS-SHA`, `develop` | `develop-20240428.123456-abc1234`, `develop` |
| **Feature branch** | `branch-name-SHA` | `feature-auth-abc1234` |
| **Pull request** | `pr-NUMBER-SHA` | `pr-42-abc1234` |
| **GitHub release** | `TAG`, `latest` | `v2.0.0`, `latest` |
| **Manual build** | Based on selection | Custom |

## 📈 Monitoring & Troubleshooting

### Check Build Status
1. **GitHub Actions**: Repository → Actions tab
2. **Docker Hub**: https://hub.docker.com/r/deepakdpk6/apigee-deployment-manager/builds

### Common Issues

#### 1. Docker Hub Authentication Failed
```
Error: push access denied, repository does not exist or may require authorization
```
**Solution**: Check `DOCKER_HUB_TOKEN` secret is correctly set

#### 2. Version Tag Already Exists
```
Error: Tag v1.0.1 already exists!
```
**Solution**: Use manual build with custom version or increment higher

#### 3. Multi-platform Build Failed
```
Error: failed to solve: failed to build for platform linux/arm64
```
**Solution**: Check Dockerfile compatibility with ARM64 architecture

### Debug Commands
```bash
# Check current tags
git tag -l

# Check Docker Hub tags
curl -s https://registry.hub.docker.com/v2/repositories/deepakdpk6/apigee-deployment-manager/tags/ | jq '.results[].name'

# Test local build
./scripts/version.sh build

# Check image metadata
docker inspect deepakdpk6/apigee-deployment-manager:latest
```

## 🔒 Security Best Practices

### Secrets Management
- ✅ Use GitHub Secrets for sensitive data
- ✅ Never commit Docker Hub tokens
- ✅ Rotate access tokens regularly
- ✅ Use least-privilege access tokens

### Docker Security
- ✅ Non-root user in container
- ✅ Minimal base image (python:3.11-slim)
- ✅ No secrets in image layers
- ✅ Multi-stage builds for smaller images

## 📚 Additional Resources

- **GitHub Actions Documentation**: https://docs.github.com/en/actions
- **Docker Hub Automated Builds**: https://docs.docker.com/docker-hub/builds/
- **Semantic Versioning**: https://semver.org/
- **Docker Multi-platform Builds**: https://docs.docker.com/build/building/multi-platform/

## 🎯 Next Steps

1. **Set up branch protection** for main branch
2. **Configure automated testing** before builds
3. **Add security scanning** to pipeline
4. **Set up monitoring** and alerting
5. **Create staging environment** for testing

---

**🚀 Your CI/CD pipeline is now ready! Every commit to main will automatically build and deploy a new Docker image with an incremented version number.**
