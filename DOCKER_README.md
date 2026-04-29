# Apigee Deployment Manager - Docker Image

[![Docker Hub](https://img.shields.io/docker/v/deepakdpk6/apigee-deployment-manager?label=Docker%20Hub)](https://hub.docker.com/r/deepakdpk6/apigee-deployment-manager)
[![Docker Image Size](https://img.shields.io/docker/image-size/deepakdpk6/apigee-deployment-manager/latest)](https://hub.docker.com/r/deepakdpk6/apigee-deployment-manager)
[![Docker Pulls](https://img.shields.io/docker/pulls/deepakdpk6/apigee-deployment-manager)](https://hub.docker.com/r/deepakdpk6/apigee-deployment-manager)

A comprehensive web application for managing Apigee API proxy and shared flow deployments with enhanced features including ZIP file uploads, revision management, and multi-environment support.

## 🚀 Quick Start

### Using Docker Run
```bash
docker run -d \
  --name apigee-deployment-manager \
  -p 5001:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -e GCP_OAUTH_TOKEN=your_token_here \
  deepakdpk6/apigee-deployment-manager:latest
```

### Using Docker Compose
```yaml
version: '3.8'
services:
  apigee-webapp:
    image: deepakdpk6/apigee-deployment-manager:latest
    container_name: apigee-deployment-webapp
    ports:
      - "5001:5000"
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=false
      - GCP_OAUTH_TOKEN=your_token_here
    restart: unless-stopped
```

## 🎯 Key Features

### 🔧 Enhanced Deployment Options
- **ZIP File Upload**: Upload new code for existing API proxies and shared flows
- **Revision Management**: Deploy specific revisions with manual input or arrow controls
- **Dual Deployment Modes**: Choose between redeploying existing revision or uploading new code
- **Conflict Resolution**: Automatic handling of deployment conflicts with override flags

### 🛠️ Multi-Environment Management
- **KVM Management**: Create, update, and delete Key-Value Maps across multiple environments
- **Target Server Management**: Manage target servers with comprehensive CRUD operations
- **Environment Synchronization**: Deploy configurations across multiple Apigee environments
- **Bulk Operations**: Perform operations on multiple environments simultaneously

### 🔍 Advanced Debugging & Monitoring
- **Real-time Logging**: Comprehensive console and backend logging for troubleshooting
- **Form Validation**: Enhanced form submission tracking and validation
- **Error Handling**: Detailed error messages and user feedback
- **Health Checks**: Built-in health monitoring and status reporting

### 🔒 Security & Best Practices
- **Environment Variables**: Secure configuration management with .env support
- **No Hardcoded Secrets**: All sensitive data managed through environment variables
- **Docker Security**: Non-root user execution and minimal attack surface
- **Input Validation**: Comprehensive input sanitization and validation

## 📋 Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GCP_OAUTH_TOKEN` | Google Cloud OAuth token for Apigee API access | Yes | - |
| `APIGEE_ORG` | Default Apigee organization | No | - |
| `APIGEE_ENV` | Default Apigee environment | No | - |
| `FLASK_ENV` | Flask environment mode | No | `production` |
| `FLASK_DEBUG` | Enable Flask debug mode | No | `false` |
| `ADMIN_USERNAME` | Admin username for authentication | No | `apigee_admin` |
| `ADMIN_PASSWORD` | Admin password for authentication | No | `ApigeeAdmin2024!` |

## 🐳 Available Tags

| Tag | Description | Size |
|-----|-------------|------|
| `latest` | Latest stable release | ~266MB |
| `v1.0.0` | Version 1.0.0 release | ~266MB |

## 📁 Volume Mounts

| Container Path | Description | Recommended Host Path |
|----------------|-------------|-----------------------|
| `/app/uploads` | File upload storage | `./uploads` |
| `/app/logs` | Application logs | `./logs` |

## 🌐 Exposed Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `5000` | HTTP | Web application interface |

## 🔧 Usage Examples

### 1. Basic Deployment
```bash
# Pull and run the image
docker pull deepakdpk6/apigee-deployment-manager:latest
docker run -d -p 5001:5000 deepakdpk6/apigee-deployment-manager:latest

# Access the application
open http://localhost:5001
```

### 2. Production Deployment with Environment Variables
```bash
docker run -d \
  --name apigee-manager \
  -p 5001:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/logs:/app/logs \
  -e GCP_OAUTH_TOKEN="$(gcloud auth print-access-token)" \
  -e APIGEE_ORG="your-org-name" \
  -e APIGEE_ENV="your-env-name" \
  -e FLASK_ENV=production \
  --restart unless-stopped \
  deepakdpk6/apigee-deployment-manager:latest
```

### 3. Development Mode
```bash
docker run -d \
  --name apigee-dev \
  -p 5001:5000 \
  -v $(pwd):/app \
  -e FLASK_DEBUG=true \
  -e FLASK_ENV=development \
  deepakdpk6/apigee-deployment-manager:latest
```

## 🏥 Health Checks

The container includes built-in health checks:
- **Endpoint**: `http://localhost:5000/`
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3
- **Start Period**: 40 seconds

## 🔍 Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   # Ensure your GCP token is valid
   gcloud auth print-access-token
   ```

2. **Permission Denied**
   ```bash
   # Check volume permissions
   chmod 755 uploads logs
   ```

3. **Container Health Check Failures**
   ```bash
   # Check container logs
   docker logs apigee-deployment-manager
   ```

### Debug Mode
```bash
# Run with debug logging
docker run -d \
  -p 5001:5000 \
  -e FLASK_DEBUG=true \
  deepakdpk6/apigee-deployment-manager:latest

# View real-time logs
docker logs -f apigee-deployment-manager
```

## 📚 Documentation

- **GitHub Repository**: [apigee-deployment-manager](https://github.com/deepak-gunasekaran/apigee-deployment-manager)
- **Docker Hub**: [deepakdpk6/apigee-deployment-manager](https://hub.docker.com/r/deepakdpk6/apigee-deployment-manager)
- **Issue Tracker**: [GitHub Issues](https://github.com/deepak-gunasekaran/apigee-deployment-manager/issues)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Docker
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏷️ Tags & Versions

- `latest` - Always points to the most recent stable release
- `v1.0.0` - Specific version releases for production use
- Development tags available for testing new features

---

**Built with ❤️ for the Apigee community**
