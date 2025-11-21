# Wary Deployment Guide

This directory contains deployment configurations for wary.

## Docker Deployment

### Quick Start

1. **Build and run with Docker Compose:**

```bash
docker-compose up -d
```

This will start:
- Wary web server on port 8000
- PostgreSQL database
- pgAdmin on port 5050 (optional)

2. **Access the services:**

- Web UI: http://localhost:8000
- API: http://localhost:8000/api
- pgAdmin: http://localhost:5050 (optional)

### Configuration

Set environment variables in a `.env` file:

```bash
# API Key for authentication
WARY_API_KEY=your-secret-api-key-here

# Database connection (optional, defaults to docker-compose settings)
DATABASE_URL=postgresql://wary:password@db:5432/wary
```

### Production Deployment

For production, update the following:

1. **Change default passwords:**
   - PostgreSQL password in `docker-compose.yml`
   - pgAdmin password
   - Set strong `WARY_API_KEY`

2. **Use environment file:**

```bash
# Create .env file
echo "WARY_API_KEY=$(openssl rand -hex 32)" > .env
```

3. **Enable SSL/TLS:**

Use a reverse proxy like Nginx or Traefik:

```yaml
# nginx.conf
server {
    listen 443 ssl;
    server_name wary.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

4. **Set up backups:**

```bash
# Backup PostgreSQL data
docker-compose exec db pg_dump -U wary wary > backup.sql

# Restore
docker-compose exec -T db psql -U wary wary < backup.sql
```

## Kubernetes Deployment

A Kubernetes deployment example:

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wary
spec:
  replicas: 3
  selector:
    matchLabels:
      app: wary
  template:
    metadata:
      labels:
        app: wary
    spec:
      containers:
      - name: wary
        image: wary:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: wary-secrets
              key: database-url
        - name: WARY_API_KEY
          valueFrom:
            secretKeyRef:
              name: wary-secrets
              key: api-key
---
apiVersion: v1
kind: Service
metadata:
  name: wary
spec:
  selector:
    app: wary
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Cloud Platforms

### Heroku

```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create my-wary-app

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set WARY_API_KEY=$(openssl rand -hex 32)

# Deploy
git push heroku main

# Open
heroku open
```

### Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Launch app
fly launch

# Deploy
fly deploy
```

### Railway

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on git push

## Monitoring

### Health Checks

```bash
# Check if service is running
curl http://localhost:8000/health
```

### Logs

```bash
# Docker Compose logs
docker-compose logs -f web

# Kubernetes logs
kubectl logs -f deployment/wary
```

### Metrics

Consider adding:
- Prometheus for metrics
- Grafana for visualization
- Sentry for error tracking

## Scaling

### Horizontal Scaling

With Docker Compose:

```bash
docker-compose up -d --scale web=3
```

With Kubernetes:

```bash
kubectl scale deployment wary --replicas=5
```

### Database Scaling

For high traffic, consider:
- Connection pooling (pgBouncer)
- Read replicas
- Managed PostgreSQL (AWS RDS, Google Cloud SQL, etc.)

## Security

1. **API Key Authentication:**
   - Set strong `WARY_API_KEY`
   - Rotate keys regularly

2. **Database Security:**
   - Use strong passwords
   - Enable SSL for database connections
   - Restrict network access

3. **HTTPS:**
   - Always use HTTPS in production
   - Use Let's Encrypt for free certificates

4. **Rate Limiting:**
   - Add rate limiting to API endpoints
   - Use nginx or a CDN

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs web

# Check database connection
docker-compose exec web python -c "import psycopg2; psycopg2.connect('postgresql://wary:password@db:5432/wary')"
```

### Database issues

```bash
# Connect to database
docker-compose exec db psql -U wary wary

# Check tables
\dt

# Check data
SELECT COUNT(*) FROM dependency_edges;
```

### Performance issues

```bash
# Check resource usage
docker stats

# Increase workers in server.py or set via env:
export GUNICORN_WORKERS=8
```
