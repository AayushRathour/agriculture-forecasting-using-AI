# 🌾 Bhoomi Puthra - Production Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying Bhoomi Puthra Agricultural Forecasting System to production.

---

## 📋 Pre-Deployment Checklist

### 1. Environment Configuration
- [ ] Copy `.env.example` to `.env`
- [ ] Generate new SECRET_KEY (never use default!)
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS` with your domain(s)
- [ ] Set up email configuration (SMTP)
- [ ] Change admin secret key from default

### 2. Database Setup
- [ ] Migrate from SQLite to PostgreSQL/MySQL (recommended)
- [ ] Run all migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Load initial data (weather, market prices)

### 3. Security Configuration
- [ ] Set up HTTPS/SSL certificate
- [ ] Configure firewall rules
- [ ] Review security settings in `settings.py`
- [ ] Set up regular database backups

### 4. Static Files
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Configure web server to serve static files
- [ ] Set up media file storage (local or cloud)

---

## 🚀 Deployment Steps

### Step 1: Generate Secret Key

```bash
# Generate a new secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output to your `.env` file:
```
SECRET_KEY=your-new-secret-key-here
```

### Step 2: Configure Environment Variables

Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

Edit `.env` with production values:
```env
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
ADMIN_EMAIL=admin@yourdomain.com
```

### Step 3: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Or manually install
pip install django==4.2.17
pip install pillow  # For image handling
```

### Step 4: Database Migration

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial data
python manage.py loaddata initial_data.json  # If you have fixtures
```

### Step 5: Collect Static Files

```bash
# Collect all static files
python manage.py collectstatic --noinput
```

### Step 6: Run Tests

```bash
# Run all tests to ensure everything works
python manage.py test forecast.tests -v 2
```

### Step 7: Configure Web Server

#### Option A: Using Gunicorn (Recommended)

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn agri_forecast.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

#### Option B: Using uWSGI

```bash
# Install uWSGI
pip install uwsgi

# Run with uWSGI
uwsgi --http :8000 --module agri_forecast.wsgi --master --processes 4
```

### Step 8: Configure Nginx (Reverse Proxy)

Create Nginx configuration (`/etc/nginx/sites-available/bhoomiputhra`):

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

    # SSL Configuration
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;

    # Security headers
    add_header X-Frame-Options "DENY";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";

    # Static files
    location /static/ {
        alias /path/to/bhoomi-puthra/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /path/to/bhoomi-puthra/media/;
        expires 30d;
    }

    # Proxy to Django application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/bhoomiputhra /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 9: Set Up Systemd Service

Create systemd service file (`/etc/systemd/system/bhoomiputhra.service`):

```ini
[Unit]
Description=Bhoomi Puthra Gunicorn Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/bhoomi-puthra
Environment="PATH=/path/to/venv/bin"
EnvironmentFile=/path/to/bhoomi-puthra/.env
ExecStart=/path/to/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    --access-logfile /path/to/bhoomi-puthra/logs/access.log \
    --error-logfile /path/to/bhoomi-puthra/logs/error.log \
    agri_forecast.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable bhoomiputhra
sudo systemctl start bhoomiputhra
sudo systemctl status bhoomiputhra
```

---

## 🔒 Security Best Practices

### 1. SSL/TLS Certificate
- Use Let's Encrypt for free SSL certificates
- Use Certbot for automatic renewal

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 2. Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 3. Regular Backups
```bash
# Backup database
python manage.py dumpdata > backup_$(date +%Y%m%d).json

# Or for PostgreSQL
pg_dump dbname > backup_$(date +%Y%m%d).sql
```

### 4. Monitor Logs
```bash
# Monitor Django logs
tail -f logs/django_errors.log

# Monitor Gunicorn logs
tail -f logs/access.log logs/error.log
```

---

## 📊 Performance Optimization

### 1. Use Redis for Caching
```bash
# Install Redis
pip install redis django-redis

# Configure in settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 2. Use PostgreSQL Instead of SQLite
```bash
# Install PostgreSQL adapter
pip install psycopg2-binary

# Configure in settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bhoomi_puthra_db',
        'USER': 'dbuser',
        'PASSWORD': 'dbpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 3. Enable Database Connection Pooling
```bash
pip install django-db-geventpool
```

---

## 🔍 Monitoring and Maintenance

### 1. Health Check Endpoint
Add a health check URL for monitoring:
```python
# In urls.py
path('health/', lambda r: HttpResponse('OK'), name='health'),
```

### 2. Error Monitoring
Consider using:
- Sentry (error tracking)
- New Relic (application performance monitoring)
- Datadog (infrastructure monitoring)

### 3. Regular Maintenance Tasks
```bash
# Clear old sessions
python manage.py clearsessions

# Optimize database
python manage.py dbshell
# Then run: VACUUM; ANALYZE; (PostgreSQL)
```

---

## 🧪 Testing Production Configuration

### Test Checklist
- [ ] Test all pages load correctly
- [ ] Test 404 error page: visit non-existent URL
- [ ] Test 500 error page: temporarily break a view
- [ ] Test static files are served correctly
- [ ] Test media uploads work
- [ ] Test authentication system
- [ ] Test admin panel at `/af-admin/`
- [ ] Run unit tests: `python manage.py test`
- [ ] Check security headers: `curl -I https://yourdomain.com`

---

## 📝 Troubleshooting

### Common Issues

1. **Static files not loading**
   ```bash
   python manage.py collectstatic --clear
   ```

2. **Permission errors**
   ```bash
   sudo chown -R www-data:www-data /path/to/project
   sudo chmod -R 755 /path/to/project
   ```

3. **Database connection errors**
   - Check database credentials in `.env`
   - Verify database server is running
   - Check firewall rules

4. **502 Bad Gateway**
   - Check if Gunicorn is running
   - Check Gunicorn logs
   - Verify socket/port configuration

---

## 🆘 Support

For issues or questions:
- Check logs: `logs/django_errors.log`
- Review Django documentation: https://docs.djangoproject.com
- Contact system administrator

---

**Last Updated:** February 2026  
**Version:** 1.0.0  
**Project:** Bhoomi Puthra - Agricultural Forecasting System
