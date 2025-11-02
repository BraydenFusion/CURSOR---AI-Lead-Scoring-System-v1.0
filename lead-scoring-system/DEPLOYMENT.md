# 🚀 Deployment Guide

Complete guide for deploying the Lead Scoring System to production.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Environment Setup](#environment-setup)
4. [Database Setup](#database-setup)
5. [Backend Deployment](#backend-deployment)
6. [Frontend Deployment](#frontend-deployment)
7. [Production Configuration](#production-configuration)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis (optional, for caching)
- Nginx (recommended for reverse proxy)
- SSL Certificate (Let's Encrypt recommended)

### Required Knowledge
- Basic Linux/Unix command line
- Understanding of environment variables
- Database administration basics
- SSL certificate management

---

## Pre-Deployment Checklist

- [ ] Database migrations tested and ready
- [ ] Environment variables configured
- [ ] SECRET_KEY generated and set
- [ ] SMTP credentials configured (for email)
- [ ] CORS origins configured
- [ ] SSL certificates obtained
- [ ] Domain DNS configured
- [ ] Firewall rules configured
- [ ] Backup strategy planned

---

## Environment Setup

### 1. Create Production User

```bash
# Create a dedicated user for the application
sudo adduser leadscoring
sudo usermod -aG sudo leadscoring
sudo su - leadscoring
```

### 2. Clone Repository

```bash
cd /home/leadscoring
git clone <your-repo-url> lead-scoring-system
cd lead-scoring-system
```

### 3. Backend Environment

```bash
cd backend

# Copy environment template
cp .env.example .env

# Generate SECRET_KEY
openssl rand -hex 32

# Edit .env with production values
nano .env
```

**Required `.env` variables:**

```env
ENVIRONMENT=production
APP_NAME=Lead Scoring System

DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/leadscoring_prod
REDIS_URL=redis://localhost:6379/0

SECRET_KEY=<generated-secret-key-here>
ACCESS_TOKEN_EXPIRE_MINUTES=1440

CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com
```

### 4. Frontend Environment

```bash
cd ../frontend

# Create production environment file
cat > .env.production << EOF
VITE_API_BASE_URL=https://api.yourdomain.com/api
EOF
```

---

## Database Setup

### 1. Install PostgreSQL

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

### 2. Create Database and User

```bash
sudo -u postgres psql

-- In PostgreSQL prompt:
CREATE DATABASE leadscoring_prod;
CREATE USER leadscoring_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE leadscoring_prod TO leadscoring_user;
\q
```

### 3. Run Migrations

```bash
cd /home/leadscoring/lead-scoring-system/backend
source venv/bin/activate

# Run all migrations
./migrate.sh upgrade

# Or manually:
alembic upgrade head
```

### 4. Create Initial Users

```bash
python create_test_users.py
```

**Important**: Change default passwords in production!

---

## Backend Deployment

### Option 1: Systemd Service (Recommended)

```bash
sudo nano /etc/systemd/system/leadscoring.service
```

**Service file:**

```ini
[Unit]
Description=Lead Scoring System Backend
After=network.target postgresql.service

[Service]
Type=simple
User=leadscoring
WorkingDirectory=/home/leadscoring/lead-scoring-system/backend
Environment="PATH=/home/leadscoring/lead-scoring-system/backend/venv/bin"
ExecStart=/home/leadscoring/lead-scoring-system/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Start service:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable leadscoring
sudo systemctl start leadscoring
sudo systemctl status leadscoring
```

### Option 2: Docker

```bash
cd /home/leadscoring/lead-scoring-system/backend
docker build -t leadscoring-backend .
docker run -d \
  --name leadscoring-backend \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  leadscoring-backend
```

### Option 3: Gunicorn (Production WSGI Server)

```bash
pip install gunicorn

# Create gunicorn config
cat > gunicorn_config.py << EOF
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
EOF

# Run with gunicorn
gunicorn -c gunicorn_config.py app.main:app
```

---

## Frontend Deployment

### 1. Build for Production

```bash
cd /home/leadscoring/lead-scoring-system/frontend
npm install
npm run build
```

This creates a `dist/` directory with optimized production files.

### 2. Serve with Nginx

```bash
sudo nano /etc/nginx/sites-available/leadscoring
```

**Nginx configuration:**

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Frontend
    root /home/leadscoring/lead-scoring-system/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

**Enable site:**

```bash
sudo ln -s /etc/nginx/sites-available/leadscoring /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## Production Configuration

### 1. Firewall Setup

```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. Database Backups

**Create backup script:**

```bash
cat > /home/leadscoring/backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/leadscoring/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
pg_dump -U leadscoring_user leadscoring_prod > $BACKUP_DIR/backup_$DATE.sql
# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
EOF

chmod +x /home/leadscoring/backup_db.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /home/leadscoring/backup_db.sh
```

### 3. Log Management

**Backend logs:**

```bash
# View logs
sudo journalctl -u leadscoring -f

# Or if using Docker
docker logs -f leadscoring-backend
```

**Nginx logs:**

```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 4. Monitoring

**Basic health check:**

```bash
# Create health check script
cat > /home/leadscoring/health_check.sh << 'EOF'
#!/bin/bash
API_URL="https://yourdomain.com/api/health"
response=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)
if [ $response -eq 200 ]; then
    echo "API is healthy"
else
    echo "API health check failed: $response"
    # Add alerting here (email, SMS, etc.)
fi
EOF

chmod +x /home/leadscoring/health_check.sh
```

---

## Monitoring & Maintenance

### Daily Tasks
- Check application logs for errors
- Monitor disk space
- Verify backups are running

### Weekly Tasks
- Review performance metrics
- Check database size
- Update dependencies (if needed)

### Monthly Tasks
- Security updates
- SSL certificate renewal (if not auto-renewed)
- Full system backup
- Performance optimization review

### Useful Commands

```bash
# Check backend status
sudo systemctl status leadscoring

# Restart backend
sudo systemctl restart leadscoring

# View logs
sudo journalctl -u leadscoring -n 100

# Check database size
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('leadscoring_prod'));"

# Check disk space
df -h

# Check memory usage
free -h
```

---

## Troubleshooting

### Backend Won't Start

1. Check logs: `sudo journalctl -u leadscoring -n 50`
2. Verify database connection: `psql -U leadscoring_user -d leadscoring_prod`
3. Check environment variables: `cat backend/.env`
4. Verify Python dependencies: `pip list`

### Database Connection Issues

1. Check PostgreSQL is running: `sudo systemctl status postgresql`
2. Verify credentials in `.env`
3. Check firewall: `sudo ufw status`
4. Test connection: `psql -U leadscoring_user -d leadscoring_prod -h localhost`

### Frontend Build Issues

1. Clear node_modules: `rm -rf node_modules package-lock.json && npm install`
2. Check environment variables
3. Verify API URL is correct
4. Check browser console for errors

### SSL Certificate Issues

1. Check certificate validity: `sudo certbot certificates`
2. Renew if needed: `sudo certbot renew`
3. Verify Nginx config: `sudo nginx -t`

---

## Quick Reference

### Service Management
```bash
# Backend
sudo systemctl start leadscoring
sudo systemctl stop leadscoring
sudo systemctl restart leadscoring
sudo systemctl status leadscoring

# PostgreSQL
sudo systemctl start postgresql
sudo systemctl restart postgresql

# Nginx
sudo systemctl restart nginx
sudo nginx -t
```

### Database Commands
```bash
# Connect to database
psql -U leadscoring_user -d leadscoring_prod

# Run migrations
cd backend && ./migrate.sh upgrade

# Backup
pg_dump -U leadscoring_user leadscoring_prod > backup.sql

# Restore
psql -U leadscoring_user leadscoring_prod < backup.sql
```

### Log Locations
- Backend: `sudo journalctl -u leadscoring`
- Nginx access: `/var/log/nginx/access.log`
- Nginx error: `/var/log/nginx/error.log`
- System: `/var/log/syslog`

---

## Security Checklist

- [ ] SECRET_KEY is unique and secure
- [ ] Database password is strong
- [ ] Firewall configured
- [ ] SSL/TLS enabled
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Regular security updates
- [ ] Backups encrypted
- [ ] Access logs reviewed regularly
- [ ] No default passwords

---

## Support

For issues or questions:
1. Check logs first
2. Review this documentation
3. Check GitHub issues
4. Contact system administrator

---

**Last Updated**: 2024
**Version**: 2.0.0

