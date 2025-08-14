# Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Social Media Automation Platform to production environments, based on the enhanced architecture and security implementations.

## Pre-Deployment Checklist

### Security Checklist
- [ ] Change default SECRET_KEY in production
- [ ] Configure proper CORS origins (remove "*" wildcard)
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set DEBUG=False in production
- [ ] Validate all API keys and tokens
- [ ] Enable rate limiting appropriate for production load
- [ ] Configure proper logging levels

### Infrastructure Checklist
- [ ] Database server configured (PostgreSQL recommended)
- [ ] Redis server for caching and task queue
- [ ] Storage solution (AWS S3 or MinIO)
- [ ] Load balancer configured (if using multiple instances)
- [ ] Monitoring and alerting set up
- [ ] Backup strategy implemented
- [ ] CI/CD pipeline configured

### Environment Configuration
- [ ] Production environment variables configured
- [ ] Database migrations tested
- [ ] External API credentials validated
- [ ] Content generation pipeline tested
- [ ] Social media API integrations verified

## Deployment Options

### Option 1: Docker Deployment (Recommended)

```bash
# Build production image
docker build -t social-media-automation:latest .

# Run with docker-compose
docker-compose -f docker-compose.prod.yml up -d

# Check deployment
docker-compose logs -f app
```

### Option 2: Traditional Server Deployment

```bash
# Run the deployment script
./deploy.sh setup

# Start the application
./deploy.sh start

# Verify deployment
./deploy.sh health
```

### Option 3: Cloud Platform Deployment

#### AWS ECS/Fargate
1. Build and push to ECR
2. Configure ECS service
3. Set up Application Load Balancer
4. Configure auto-scaling

#### Google Cloud Run
1. Build and push to GCR
2. Deploy to Cloud Run
3. Configure custom domain
4. Set up Cloud SQL integration

#### Azure Container Instances
1. Build and push to ACR
2. Deploy to ACI
3. Configure Application Gateway
4. Set up Azure Database for PostgreSQL

## Environment Variables for Production

```bash
# Application Settings
SECRET_KEY=your-production-secret-key-32-chars-min
DEBUG=False
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=["https://yourdomain.com"]

# Database
DATABASE_URL=postgresql://user:pass@prod-db:5432/social_automation

# Redis
REDIS_URL=redis://prod-redis:6379/0

# Security Settings
RATE_LIMIT_CALLS=1000
RATE_LIMIT_PERIOD=3600
MAX_REQUEST_SIZE_MB=50

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
LOG_LEVEL=INFO
LOG_FORMAT=json

# Performance
CACHE_TTL_SECONDS=3600
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# External Services
OPENAI_API_KEY=your-production-openai-key
ELEVENLABS_API_KEY=your-production-elevenlabs-key
# ... other API keys
```

## Database Setup

### PostgreSQL Configuration

```sql
-- Create production database
CREATE DATABASE social_automation;
CREATE USER app_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE social_automation TO app_user;

-- Configure connection limits
ALTER USER app_user CONNECTION LIMIT 50;
```

### Migration Process

```bash
# Backup existing data (if upgrading)
pg_dump social_automation > backup_$(date +%Y%m%d_%H%M%S).sql

# Run migrations
alembic upgrade head

# Verify migration
python -c "
from src.core.database import engine
from src.models import Base
import asyncio

async def verify():
    async with engine.begin() as conn:
        result = await conn.execute('SELECT COUNT(*) FROM information_schema.tables')
        print(f'Tables created: {result.scalar()}')

asyncio.run(verify())
"
```

## Load Balancer Configuration

### Nginx Configuration

```nginx
upstream social_media_app {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;  # If running multiple instances
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/private.key;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    location / {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://social_media_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Health checks
    location /health {
        access_log off;
        proxy_pass http://social_media_app;
    }
    
    # Static files (if any)
    location /static/ {
        alias /path/to/static/files/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### AWS Application Load Balancer

```yaml
# ALB Target Group
TargetGroup:
  Type: AWS::ElasticLoadBalancingV2::TargetGroup
  Properties:
    Name: social-media-automation-tg
    Protocol: HTTP
    Port: 8000
    VpcId: !Ref VPC
    HealthCheckPath: /health
    HealthCheckProtocol: HTTP
    HealthCheckIntervalSeconds: 30
    HealthyThresholdCount: 2
    UnhealthyThresholdCount: 5
    TargetType: ip

# Application Load Balancer
LoadBalancer:
  Type: AWS::ElasticLoadBalancingV2::LoadBalancer
  Properties:
    Name: social-media-automation-alb
    Scheme: internet-facing
    Type: application
    SecurityGroups:
      - !Ref ALBSecurityGroup
    Subnets:
      - !Ref PublicSubnet1
      - !Ref PublicSubnet2
```

## Monitoring and Alerting

### Application Monitoring

```python
# Prometheus metrics endpoint
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_duration_seconds', 'Request latency')

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path
    ).inc()
    
    REQUEST_LATENCY.observe(time.time() - start_time)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Log Aggregation

```yaml
# Docker Compose with centralized logging
version: '3.8'
services:
  app:
    image: social-media-automation:latest
    logging:
      driver: "fluentd"
      options:
        fluentd-address: localhost:24224
        tag: social.media.app
    
  fluentd:
    image: fluent/fluentd:v1.14
    volumes:
      - ./fluentd/conf:/fluentd/etc
    ports:
      - "24224:24224"
    
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.15.0
    environment:
      - discovery.type=single-node
    
  kibana:
    image: docker.elastic.co/kibana/kibana:7.15.0
    ports:
      - "5601:5601"
```

## Performance Optimization

### Database Optimization

```sql
-- Create indexes for common queries
CREATE INDEX CONCURRENTLY idx_content_created_at ON content(created_at);
CREATE INDEX CONCURRENTLY idx_content_status ON content(status);
CREATE INDEX CONCURRENTLY idx_analytics_date ON analytics(date);

-- Analyze tables for query optimization
ANALYZE content;
ANALYZE analytics;
ANALYZE projects;
```

### Redis Configuration

```conf
# redis.conf for production
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000

# Network settings
tcp-keepalive 300
timeout 0

# Security
requirepass your-redis-password
```

### Caching Strategy

```python
# Implement intelligent caching
@cached(ttl=3600, key_prefix="content_generation")
async def generate_content_cached(prompt: str, style: str):
    return await ai_service.generate_content(prompt, style)

@cached(ttl=1800, key_prefix="analytics_data")
async def get_analytics_cached(start_date: str, end_date: str):
    return await analytics_service.get_data(start_date, end_date)
```

## Security Configuration

### SSL/TLS Setup

```bash
# Let's Encrypt with Certbot
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Firewall Configuration

```bash
# UFW firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Application-specific rules
sudo ufw allow from 10.0.0.0/8 to any port 8000  # Internal ALB access
```

### Environment Security

```bash
# Secure environment file
sudo chown root:app-group /etc/social-media-automation/.env
sudo chmod 640 /etc/social-media-automation/.env

# Use systemd environment files
sudo systemctl edit social-media-automation
# Add environment file reference
```

## Backup and Recovery

### Database Backup

```bash
#!/bin/bash
# backup.sh
DB_NAME="social_automation"
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
pg_dump $DB_NAME | gzip > "$BACKUP_DIR/backup_$DATE.sql.gz"

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp "$BACKUP_DIR/backup_$DATE.sql.gz" s3://your-backup-bucket/postgres/
```

### Application Data Backup

```bash
# Content files backup
rsync -av --delete /path/to/content/files/ /backups/content/

# Configuration backup
tar -czf /backups/config_$DATE.tar.gz /etc/social-media-automation/
```

## Troubleshooting

### Common Issues

1. **High Memory Usage**
   ```bash
   # Monitor memory usage
   ps aux --sort=-%mem | head -20
   
   # Check for memory leaks
   curl http://localhost:8000/health/detailed | jq '.components.memory'
   ```

2. **Database Connection Issues**
   ```bash
   # Check database connectivity
   pg_isready -h db-host -p 5432 -U username
   
   # Monitor connections
   psql -c "SELECT count(*) FROM pg_stat_activity;"
   ```

3. **Redis Connection Issues**
   ```bash
   # Test Redis connectivity
   redis-cli -h redis-host ping
   
   # Monitor Redis memory
   redis-cli info memory
   ```

### Performance Issues

1. **Slow API Responses**
   ```bash
   # Check performance metrics
   curl http://localhost:8000/metrics | grep request_duration
   
   # Analyze slow queries
   tail -f logs/app.log | grep "slow_query"
   ```

2. **High CPU Usage**
   ```bash
   # Profile application
   py-spy top --pid $(pgrep -f "uvicorn")
   
   # Check system load
   uptime && iostat 1 5
   ```

## Maintenance

### Regular Maintenance Tasks

```bash
# Weekly maintenance script
#!/bin/bash

# Clean up old logs
find /var/log/social-media-automation/ -name "*.log" -mtime +7 -delete

# Clean up temporary files
find /tmp/generated_content/ -mtime +1 -delete

# Vacuum database
psql social_automation -c "VACUUM ANALYZE;"

# Clear expired cache entries
redis-cli --eval "
local keys = redis.call('keys', ARGV[1])
for i=1,#keys,5000 do
    redis.call('del', unpack(keys, i, math.min(i+4999, #keys)))
end
" 0 "cache:*"

# Update system packages (if approved)
# sudo apt-get update && sudo apt-get upgrade -y
```

### Health Monitoring

```bash
# Continuous health monitoring
#!/bin/bash
while true; do
    if ! curl -s http://localhost:8000/health | grep -q "healthy"; then
        echo "$(date): Health check failed" >> /var/log/health-monitor.log
        # Send alert (email, Slack, etc.)
    fi
    sleep 30
done
```

## Rollback Procedures

### Application Rollback

```bash
# Docker rollback
docker tag social-media-automation:latest social-media-automation:backup
docker pull social-media-automation:previous
docker stop social-media-app
docker run -d --name social-media-app social-media-automation:previous

# Traditional deployment rollback
git checkout previous-stable-tag
./deploy.sh restart
```

### Database Rollback

```bash
# Database rollback (use with extreme caution)
psql social_automation < backup_before_deployment.sql
alembic downgrade -1  # Rollback one migration
```

This production deployment guide provides comprehensive instructions for deploying the enhanced Social Media Automation Platform with all the security, monitoring, and performance improvements implemented.