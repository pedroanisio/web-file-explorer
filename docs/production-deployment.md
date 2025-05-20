# Production Deployment Guide

This guide provides instructions for deploying the Python File Explorer application in a production environment.

## Prerequisites

- Docker and Docker Compose (v2.x+)
- Access to a Linux server with SSH
- Domain name (optional but recommended)
- SSL certificate (optional but recommended for HTTPS)

## Deployment Methods

### 1. Manual Deployment

#### Setup Environment

1. Clone the repository to your server:
   ```bash
   git clone https://github.com/yourusername/python-file-explorer-app.git
   cd python-file-explorer-app
   ```

2. Create `.env.prod` file from the example:
   ```bash
   cp env.prod.example .env.prod
   ```

3. Edit the environment variables in `.env.prod` to match your environment:
   ```bash
   nano .env.prod
   ```

#### SSL Configuration

1. Create directories for SSL certificates:
   ```bash
   mkdir -p nginx/ssl
   ```

2. Copy your SSL certificates into the `nginx/ssl` directory:
   ```bash
   cp /path/to/your/certificate.pem nginx/ssl/cert.pem
   cp /path/to/your/key.pem nginx/ssl/key.pem
   ```

#### Launch the Application

1. Start the services with production configuration:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

2. Verify the application is running:
   ```bash
   docker-compose ps
   ```

3. Test the application by navigating to your domain or server IP.

### 2. CI/CD Deployment

For automated deployments, we use GitHub Actions workflows.

#### Required Secrets

Set up the following secrets in your GitHub repository:

**Docker Hub**:
- `DOCKERHUB_USERNAME`: Your Docker Hub username
- `DOCKERHUB_TOKEN`: Your Docker Hub access token

**Staging Environment**:
- `STAGING_HOST`: The hostname or IP of your staging server
- `STAGING_USER`: SSH username
- `STAGING_SSH_KEY`: SSH private key for the staging server
- `STAGING_DEPLOY_PATH`: Path to the project on the staging server

**Production Environment**:
- `PRODUCTION_HOST`: The hostname or IP of your production server
- `PRODUCTION_USER`: SSH username
- `PRODUCTION_SSH_KEY`: SSH private key for production server
- `PRODUCTION_DEPLOY_PATH`: Path to the project on the production server
- `PRODUCTION_URL`: The URL of your production application
- `ENV_PROD`: The entire contents of your production .env.prod file

**AWS (if using ECR)**:
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret access key
- `AWS_REGION`: AWS region

**Notifications**:
- `SLACK_WEBHOOK_URL`: Slack webhook URL for notifications

#### Workflow

The CI/CD workflow will:

1. Run tests and linting on each PR and push
2. Build Docker images for develop and main branches
3. Deploy to staging automatically after successful builds
4. Deploy to production after staging is successful

## Server Requirements

- Minimum 1 CPU / 1GB RAM (recommended: 2 CPU / 2GB RAM)
- 10GB disk space
- Ubuntu 20.04+ or similar Linux distribution
- Ports 80 and 443 open in the firewall

## Scaling and Performance

The application can be scaled horizontally by increasing the number of replicas:

```bash
REPLICAS=3 docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Monitoring and Logging

Logs can be viewed using:

```bash
docker-compose logs -f
```

For more advanced monitoring, consider integrating with:
- Prometheus for metrics
- Grafana for visualization
- ELK stack for log aggregation

## Backup and Restore

### Backup

```bash
# Backup the data directory
tar -czf file-explorer-data-backup-$(date +%Y%m%d).tar.gz /path/to/data/directory

# Backup environment variables
cp .env.prod .env.prod-backup-$(date +%Y%m%d)
```

### Restore

```bash
# Restore the data directory
tar -xzf file-explorer-data-backup-YYYYMMDD.tar.gz -C /path/to/restore/

# Restore environment variables
cp .env.prod-backup-YYYYMMDD .env.prod
```

## Troubleshooting

### Common Issues

1. **Application not accessible**:
   - Check if containers are running: `docker-compose ps`
   - Verify Nginx configuration
   - Check firewall settings

2. **Permission errors**:
   - Ensure proper permissions on mounted volumes
   - Check that the nonroot user has access to directories

3. **SSL issues**:
   - Verify SSL certificate paths in Nginx configuration
   - Ensure certificates are valid and not expired

### Logs

Check application logs:
```bash
docker-compose logs file-explorer
```

Check Nginx logs:
```bash
docker-compose logs nginx
```

## Maintenance

### Updates

To update to the latest version:

```bash
git pull
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Cleanup

To clean up unused Docker resources:

```bash
docker system prune -af --volumes
```

## Security Considerations

- Regularly update the application and its dependencies
- Use strong passwords for environment variables
- Run the application as a non-root user (already configured)
- Implement proper firewall rules
- Set up fail2ban to protect against brute force attacks
- Consider using a Web Application Firewall (WAF) 