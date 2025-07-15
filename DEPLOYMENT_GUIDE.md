# 🚀 Opero Platform - Complete Deployment Guide

Welcome to the comprehensive deployment guide for your Opero AI-powered business automation platform! This guide covers all 6 deployment tasks with step-by-step instructions.

## 📋 Table of Contents

1. [Production Configuration](#1-production-configuration)
2. [Docker Containerization](#2-docker-containerization)
3. [Cloud Deployment](#3-cloud-deployment)
4. [Domain & SSL Setup](#4-domain--ssl-setup)
5. [Performance Optimization](#5-performance-optimization)
6. [Monitoring & Analytics](#6-monitoring--analytics)

---

## 1. 🔧 Production Configuration

### Environment Variables Setup

1. **Copy the production environment template:**
   ```bash
   cp .env.production.example .env.production
   ```

2. **Edit `.env.production` with your actual values:**
   ```bash
   nano .env.production
   ```

3. **Required configurations:**
   - **SECRET_KEY**: Generate with `openssl rand -hex 32`
   - **JWT_SECRET_KEY**: Generate with `openssl rand -hex 32`
   - **DATABASE_URL**: Your production PostgreSQL connection string
   - **REDIS_URL**: Your production Redis connection string
   - **OPENAI_API_KEY**: Your OpenAI API key for AI features
   - **ALLOWED_HOSTS**: Your domain names
   - **CORS_ORIGINS**: Your frontend domains

### Security Headers
The configuration automatically includes:
- HTTPS enforcement
- Security headers (XSS protection, CSRF protection)
- Rate limiting
- Input validation

---

## 2. 🐳 Docker Containerization

### Development Environment

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

### Production Environment

```bash
# Build production images
docker-compose -f docker-compose.production.yml build

# Start production environment
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose -f docker-compose.production.yml ps
```

### Environment Variables for Docker
Create `.env` file in the same directory as docker-compose files:
```bash
DB_PASSWORD=your-secure-db-password
REDIS_PASSWORD=your-secure-redis-password
GRAFANA_PASSWORD=your-grafana-admin-password
```

---

## 3. ☁️ Cloud Deployment

### Option A: AWS Deployment

1. **Prerequisites:**
   ```bash
   # Install AWS CLI
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   
   # Configure AWS credentials
   aws configure
   ```

2. **Deploy to AWS:**
   ```bash
   chmod +x deployment/deploy-aws.sh
   ./deployment/deploy-aws.sh
   ```

3. **Post-deployment:**
   - Configure Route 53 for your domain
   - Set up CloudWatch logging
   - Configure auto-scaling policies

### Option B: Google Cloud Platform

1. **Prerequisites:**
   ```bash
   # Install gcloud CLI
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   gcloud init
   ```

2. **Deploy to GCP:**
   ```bash
   # Update PROJECT_ID in the script
   nano deployment/deploy-gcp.sh
   
   chmod +x deployment/deploy-gcp.sh
   ./deployment/deploy-gcp.sh
   ```

### Option C: Azure Deployment

1. **Prerequisites:**
   ```bash
   # Install Azure CLI
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   az login
   ```

2. **Deploy to Azure:**
   ```bash
   chmod +x deployment/deploy-azure.sh
   ./deployment/deploy-azure.sh
   ```

---

## 4. 🌐 Domain & SSL Setup

### Domain Configuration

1. **Point your domain to your server:**
   - A Record: `yourdomain.com` → `your-server-ip`
   - A Record: `www.yourdomain.com` → `your-server-ip`
   - A Record: `api.yourdomain.com` → `your-server-ip`

### SSL Certificate Setup

1. **Automatic SSL with Let's Encrypt:**
   ```bash
   # Update domain and email in the script
   nano deployment/setup-ssl.sh
   
   chmod +x deployment/setup-ssl.sh
   sudo ./deployment/setup-ssl.sh
   ```

2. **Manual SSL Certificate:**
   ```bash
   # If you have your own certificates
   sudo cp your-cert.pem /etc/nginx/ssl/fullchain.pem
   sudo cp your-key.pem /etc/nginx/ssl/privkey.pem
   sudo chown root:root /etc/nginx/ssl/*
   sudo chmod 644 /etc/nginx/ssl/fullchain.pem
   sudo chmod 600 /etc/nginx/ssl/privkey.pem
   ```

### Nginx Configuration

1. **Update domain in nginx config:**
   ```bash
   nano nginx/nginx.conf
   # Replace 'yourdomain.com' with your actual domain
   ```

2. **Deploy nginx configuration:**
   ```bash
   sudo cp nginx/nginx.conf /etc/nginx/nginx.conf
   sudo nginx -t
   sudo systemctl reload nginx
   ```

---

## 5. ⚡ Performance Optimization

### Database Optimization

1. **PostgreSQL Tuning:**
   ```sql
   -- Connect to your database and run:
   ALTER SYSTEM SET shared_buffers = '256MB';
   ALTER SYSTEM SET effective_cache_size = '1GB';
   ALTER SYSTEM SET work_mem = '4MB';
   ALTER SYSTEM SET maintenance_work_mem = '64MB';
   SELECT pg_reload_conf();
   ```

2. **Connection Pooling:**
   The application uses SQLAlchemy connection pooling (configured in `performance.py`)

### Redis Caching

1. **Redis Configuration:**
   ```bash
   # Redis memory optimization
   redis-cli CONFIG SET maxmemory 512mb
   redis-cli CONFIG SET maxmemory-policy allkeys-lru
   ```

2. **Cache Warming:**
   ```bash
   # Warm up frequently accessed endpoints
   curl http://localhost:8000/contacts/stats/overview
   curl http://localhost:8000/agent/analytics
   ```

### Application Performance

1. **Enable Gunicorn for production:**
   ```bash
   # Already configured in Dockerfile.production
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

2. **Background Tasks:**
   ```bash
   # Start Celery worker for background tasks
   celery -A app.core.performance worker --loglevel=info
   ```

---

## 6. 📊 Monitoring & Analytics

### Prometheus & Grafana Setup

1. **Start monitoring stack:**
   ```bash
   docker-compose -f docker-compose.production.yml --profile monitoring up -d
   ```

2. **Access monitoring dashboards:**
   - Prometheus: `http://your-domain:9090`
   - Grafana: `http://your-domain:3000` (admin/password from env)

### Application Monitoring

1. **Health checks:**
   ```bash
   curl http://your-domain/monitoring/health
   curl http://your-domain/monitoring/metrics/system
   curl http://your-domain/monitoring/metrics/application
   ```

2. **Log monitoring:**
   ```bash
   # View recent logs
   curl http://your-domain/monitoring/logs/recent
   
   # Check for alerts
   curl http://your-domain/monitoring/alerts
   ```

### Error Tracking with Sentry

1. **Set up Sentry:**
   - Create account at sentry.io
   - Create new project
   - Add SENTRY_DSN to your `.env.production`

2. **Test error tracking:**
   ```python
   # Sentry will automatically capture errors
   import sentry_sdk
   sentry_sdk.capture_message("Test message from Opero")
   ```

---

## 🔐 Security Checklist

### Pre-deployment Security
- [ ] Generate strong secret keys (32+ characters)
- [ ] Configure HTTPS-only cookies
- [ ] Set up proper CORS origins
- [ ] Enable rate limiting
- [ ] Configure security headers

### Database Security
- [ ] Use strong database passwords
- [ ] Enable SSL connections
- [ ] Restrict database access by IP
- [ ] Regular database backups
- [ ] Encrypt sensitive data

### Infrastructure Security
- [ ] Keep Docker images updated
- [ ] Use non-root containers
- [ ] Configure firewall rules
- [ ] Enable audit logging
- [ ] Regular security updates

---

## 🚀 Deployment Checklist

### Pre-deployment
- [ ] All environment variables configured
- [ ] DNS records pointing to server
- [ ] SSL certificates ready
- [ ] Database initialized
- [ ] Redis cache configured

### Deployment
- [ ] Application deployed successfully
- [ ] Database migrations completed
- [ ] Static files served correctly
- [ ] All endpoints responding
- [ ] Health checks passing

### Post-deployment
- [ ] Monitoring dashboards configured
- [ ] Alerts set up
- [ ] Backup procedures tested
- [ ] Performance benchmarks established
- [ ] Documentation updated

---

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Errors:**
   ```bash
   # Check database status
   docker-compose exec db pg_isready -U opero_user
   
   # Check connection string
   echo $DATABASE_URL
   ```

2. **SSL Certificate Issues:**
   ```bash
   # Test SSL
   openssl s_client -connect yourdomain.com:443
   
   # Check certificate expiration
   openssl x509 -in /etc/nginx/ssl/fullchain.pem -text -noout
   ```

3. **Performance Issues:**
   ```bash
   # Check resource usage
   docker stats
   
   # Check application logs
   docker-compose logs api
   ```

### Getting Help

- **Application Logs:** `/app/logs/opero.log`
- **Error Logs:** `/app/logs/opero_errors.log`
- **Nginx Logs:** `/var/log/nginx/`
- **System Logs:** `journalctl -u docker`

---

## 🎉 Success!

Your Opero platform should now be:

✅ **Secure**: HTTPS, security headers, rate limiting  
✅ **Scalable**: Docker containers, load balancing  
✅ **Monitored**: Health checks, metrics, alerts  
✅ **Performant**: Caching, connection pooling, optimization  
✅ **Reliable**: Error tracking, logging, backups  

### Next Steps

1. **Custom Domain**: Point your domain to the deployment
2. **Content**: Add your business content and branding
3. **Features**: Customize AI agent responses and workflows
4. **Analytics**: Set up business intelligence dashboards
5. **Marketing**: Launch your platform to users!

---

**🚀 Welcome to production with Opero! Your AI-powered business automation platform is now live and ready to streamline operations for your users.**
