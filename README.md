# Apigee Deployment Web Application

A comprehensive web application for managing Apigee API proxies, shared flows, target servers, and KVMs with Docker support.

## Features

- **Authentication**: Basic auth with static credentials
- **GCP Integration**: Token-based authentication with Google Cloud Platform
- **Deployment**: Upload and deploy new API proxies and shared flows
- **Management**: Update target servers and KVM entries
- **Organization Management**: Browse organizations and environments
- **File Upload**: Support for ZIP bundle uploads (up to 50MB)
- **Responsive UI**: Modern Bootstrap-based interface

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- GCP access token (obtain with `gcloud auth print-access-token`)

### Run the Application

1. **Build and start the container:**
   ```bash
   cd /Users/AL42930/APG-HYB-EKS/apigee-deployment-webapp
   docker-compose up --build
   ```

2. **Access the application:**
   - URL: http://localhost:5000
   - Username: `apigee_admin`
   - Password: `ApigeeAdmin2024!`

3. **Configure GCP token:**
   - Navigate to "GCP Authentication"
   - Paste your GCP access token
   - Click "Validate & Save Token"

## Manual Installation

### Prerequisites
- Python 3.11+
- pip

### Setup
```bash
cd /Users/AL42930/APG-HYB-EKS/apigee-deployment-webapp
pip install -r requirements.txt
python app.py
```

## Usage

### 1. Authentication
- Login with credentials: `apigee_admin` / `ApigeeAdmin2024!`
- Configure your GCP access token in the Auth section

### 2. Deploy API Proxies/Shared Flows
- Select organization and environment
- Choose deployment type (API Proxy or Shared Flow)
- Upload new ZIP bundle or deploy existing resources
- Monitor deployment status

### 3. Manage Resources
- View and update target servers
- Manage KVM entries
- Browse organizations and environments

## API Endpoints

- `GET /api/organizations` - List organizations
- `GET /api/organizations/{org}/environments` - List environments
- `GET /api/organizations/{org}/apis` - List API proxies
- `GET /api/organizations/{org}/sharedflows` - List shared flows
- `GET /api/organizations/{org}/environments/{env}/targetservers` - List target servers
- `GET /api/organizations/{org}/environments/{env}/keyvaluemaps` - List KVMs
- `PUT /api/organizations/{org}/environments/{env}/targetservers/{server}` - Update target server
- `POST /api/organizations/{org}/environments/{env}/keyvaluemaps/{kvm}/entries` - Update KVM entry

## Docker Configuration

### Environment Variables
- `FLASK_ENV=production`
- `FLASK_DEBUG=false`

### Volumes
- `./uploads:/app/uploads` - File upload storage
- `./logs:/app/logs` - Application logs

### Health Check
- Endpoint: `http://localhost:5000/`
- Interval: 30 seconds
- Timeout: 10 seconds

## Security

- Basic authentication with hashed passwords
- File upload validation (ZIP files only)
- Secure filename handling
- Non-root container user
- Session-based token storage

## File Structure

```
apigee-deployment-webapp/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
├── .dockerignore         # Docker ignore rules
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── login.html        # Login page
│   ├── dashboard.html    # Dashboard
│   ├── auth.html         # GCP authentication
│   ├── deploy.html       # Deployment interface
│   └── manage.html       # Resource management
├── uploads/              # File upload directory
└── logs/                 # Application logs
```

## Troubleshooting

### Common Issues

1. **Token Expired**: GCP tokens expire after 1 hour. Refresh with `gcloud auth print-access-token`

2. **File Upload Fails**: Ensure ZIP files are under 50MB and properly formatted

3. **API Errors**: Check GCP token validity and organization permissions

4. **Container Issues**: Check Docker logs with `docker-compose logs`

### Logs
- Application logs: `./logs/`
- Docker logs: `docker-compose logs apigee-webapp`

## Development

### Local Development
```bash
export FLASK_ENV=development
export FLASK_DEBUG=true
python app.py
```

### Adding Features
- Extend API endpoints in `app.py`
- Add new templates in `templates/`
- Update requirements in `requirements.txt`

## License

Internal use only - Apigee Deployment Manager
