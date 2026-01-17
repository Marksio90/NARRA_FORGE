# NARRA_FORGE V2 Deployment Guide

Complete guide for deploying NARRA_FORGE V2 to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Environment Configuration](#environment-configuration)
4. [Docker Deployment](#docker-deployment)
5. [SSL/TLS Setup](#ssltls-setup)
6. [Monitoring](#monitoring)
7. [Backup & Restore](#backup--restore)
8. [Maintenance](#maintenance)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### Hardware Requirements

**Minimum (Small-scale production)**
- 2 CPU cores
- 4 GB RAM
- 20 GB storage
- Ubuntu 20.04 or later

**Recommended (Production)**
- 4+ CPU cores
- 8+ GB RAM
- 100+ GB SSD storage
- Ubuntu 22.04 LTS

### Software Requirements

- Docker 24.0+
- Docker Compose 2.20+
- Git
- Domain name with DNS configured
- SMTP server (for email notifications)

## Server Setup

### 1. Update System

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 2. Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt-get install docker-compose-plugin
```

### 3. Install Required Tools

```bash
sudo apt-get install -y git curl wget htop
```

### 4. Configure Firewall

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

## Environment Configuration

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/NARRA_FORGE.git
cd NARRA_FORGE
```

### 2. Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Required Variables:**

```env
# Database
DB_PASSWORD=<strong-password>

# Security
JWT_SECRET_KEY=<min-32-character-random-string>
REDIS_PASSWORD=<strong-password>

# API Keys
OPENAI_API_KEY=<your-key>
ANTHROPIC_API_KEY=<your-key>

# Monitoring
SENTRY_DSN=<your-sentry-dsn>

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# Grafana
GRAFANA_PASSWORD=<strong-password>
```

### 3. Generate Secrets

```bash
# Generate JWT secret (32+ characters)
openssl rand -hex 32

# Generate passwords
openssl rand -base64 24
```

## Docker Deployment

### Development Deployment

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment

```bash
# Use deployment script
./scripts/deploy.sh production

# Or manually
docker-compose -f docker-compose.prod.yml up -d
```

### Verify Deployment

```bash
# Check running containers
docker-compose -f docker-compose.prod.yml ps

# Test API health
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000
```

## SSL/TLS Setup

### Using Let's Encrypt (Recommended)

```bash
# Run SSL setup script
./scripts/setup-ssl.sh yourdomain.com admin@yourdomain.com
```

### Manual Certificate Installation

```bash
# Copy certificates to nginx/ssl/
cp your-cert.pem nginx/ssl/cert.pem
cp your-key.pem nginx/ssl/key.pem

# Set permissions
chmod 644 nginx/ssl/cert.pem
chmod 600 nginx/ssl/key.pem

# Restart nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

## Monitoring

### Access Monitoring Services

- **Grafana**: `https://yourdomain.com:3000`
  - Default credentials: admin / `<GRAFANA_PASSWORD from .env>`

- **Prometheus**: `http://localhost:9090` (internal)

### Key Metrics to Monitor

- API response times
- Database connections
- Celery queue length
- Memory/CPU usage
- Error rates

### Configure Alerts

Edit `monitoring/prometheus.yml` to add alert rules.

## Backup & Restore

### Create Backup

```bash
# Manual backup
./scripts/backup.sh

# Backups are saved to: /backups/narra_forge_backup_YYYYMMDD_HHMMSS.sql.gz
```

### Schedule Automatic Backups

```bash
# Add to crontab
crontab -e

# Add daily backup at 3 AM
0 3 * * * cd /path/to/NARRA_FORGE && ./scripts/backup.sh
```

### Restore from Backup

```bash
# List available backups
ls -lh /backups/

# Restore
./scripts/restore.sh /backups/narra_forge_backup_20260117_030000.sql.gz
```

## Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
./scripts/deploy.sh production
```

### Database Migrations

```bash
# Create new migration
docker-compose -f docker-compose.prod.yml exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Rollback migration
docker-compose -f docker-compose.prod.yml exec backend alembic downgrade -1
```

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### Restart Services

```bash
# Restart all
docker-compose -f docker-compose.prod.yml restart

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend
```

## Scaling

### Horizontal Scaling

Edit `docker-compose.prod.yml` to adjust replicas:

```yaml
backend:
  deploy:
    replicas: 4  # Increase for more backend instances

celery_worker:
  deploy:
    replicas: 4  # Increase for more workers
```

### Vertical Scaling

Adjust resource limits:

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
```

## Troubleshooting

### Services Won't Start

```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs

# Verify environment variables
docker-compose -f docker-compose.prod.yml config
```

### Database Connection Issues

```bash
# Check PostgreSQL logs
docker-compose -f docker-compose.prod.yml logs postgres

# Test connection
docker-compose -f docker-compose.prod.yml exec postgres psql -U narra_forge -c "SELECT 1"
```

### High Memory Usage

```bash
# Check resource usage
docker stats

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

### SSL Certificate Issues

```bash
# Check certificate validity
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Renew certificate
./scripts/renew-ssl.sh
```

## Security Checklist

- [ ] Strong passwords for all services
- [ ] JWT secret is random and secure (32+ characters)
- [ ] SSL/TLS enabled with valid certificate
- [ ] Firewall configured (only 22, 80, 443 open)
- [ ] Regular backups scheduled
- [ ] Monitoring and alerts configured
- [ ] Database connections limited to internal network
- [ ] CORS origins properly configured
- [ ] Rate limiting enabled
- [ ] Sentry error tracking enabled

## Performance Optimization

### Database

```bash
# Analyze query performance
docker-compose -f docker-compose.prod.yml exec postgres psql -U narra_forge -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

### Redis

```bash
# Check memory usage
docker-compose -f docker-compose.prod.yml exec redis redis-cli INFO memory
```

### Nginx

- Enable caching for static assets
- Configure gzip compression
- Optimize worker processes

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/NARRA_FORGE/issues
- Documentation: https://docs.narraforge.com
- Email: support@narraforge.com
