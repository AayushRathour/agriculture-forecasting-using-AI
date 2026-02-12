# 🌾 Bhoomi Puthra - Quick Production Commands

## 🚀 Deployment Commands

### Initial Setup
```bash
# 1. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 4. Copy environment file
cp .env.example .env
# Edit .env with your production values

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Collect static files
python manage.py collectstatic --noinput
```

### Security Check
```bash
# Run deployment security check
$env:DEBUG="False"  # Windows
export DEBUG=False  # Linux/Mac
python manage.py check --deploy
```

### Testing
```bash
# Run all tests
python manage.py test forecast.tests -v 2

# Run specific test class
python manage.py test forecast.tests.RecommendationLogicTests

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Static Files
```bash
# Collect static files
python manage.py collectstatic --noinput

# Clear and recollect
python manage.py collectstatic --clear --noinput
```

### Database Operations
```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create backup
python manage.py dumpdata > backup.json

# Load data
python manage.py loaddata backup.json

# Database shell
python manage.py dbshell
```

### Running Production Server
```bash
# With Gunicorn (recommended)
gunicorn agri_forecast.wsgi:application --bind 0.0.0.0:8000 --workers 4

# With more options
gunicorn agri_forecast.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --daemon

# With uWSGI
uwsgi --http :8000 --module agri_forecast.wsgi --master --processes 4
```

### Systemd Service Management
```bash
# Start service
sudo systemctl start bhoomiputhra

# Stop service
sudo systemctl stop bhoomiputhra

# Restart service
sudo systemctl restart bhoomiputhra

# Check status
sudo systemctl status bhoomiputhra

# Enable on boot
sudo systemctl enable bhoomiputhra

# View logs
sudo journalctl -u bhoomiputhra -f
```

### Nginx Management
```bash
# Test configuration
sudo nginx -t

# Reload configuration
sudo systemctl reload nginx

# Restart Nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx
```

### SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Renew certificate (dry run)
sudo certbot renew --dry-run

# Auto-renewal is handled by systemd timer
sudo systemctl status certbot.timer
```

### Monitoring & Logs
```bash
# View Django error logs
tail -f logs/django_errors.log

# View Gunicorn logs
tail -f logs/access.log
tail -f logs/error.log

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Clear old sessions
python manage.py clearsessions
```

### Database Maintenance (PostgreSQL)
```bash
# Connect to database
psql -U dbuser -d bhoomi_puthra_db

# Backup database
pg_dump bhoomi_puthra_db > backup_$(date +%Y%m%d).sql

# Restore database
psql -U dbuser -d bhoomi_puthra_db < backup.sql

# Optimize database
psql -U dbuser -d bhoomi_puthra_db -c "VACUUM ANALYZE;"
```

### Environment Variables
```bash
# Set for current session (Windows)
$env:DEBUG="False"
$env:SECRET_KEY="your-secret-key"
$env:ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"

# Set for current session (Linux/Mac)
export DEBUG=False
export SECRET_KEY="your-secret-key"
export ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"

# Load from .env file (using python-decouple)
# Just create .env file and it will be loaded automatically
```

### User Management
```bash
# Create superuser
python manage.py createsuperuser

# Change user password
python manage.py changepassword username

# Shell with Django context
python manage.py shell
```

### Performance Testing
```bash
# Install locust
pip install locust

# Run load test
locust -f locustfile.py --host=http://localhost:8000
```

### Docker Commands (if using Docker)
```bash
# Build image
docker build -t bhoomiputhra:latest .

# Run container
docker run -d -p 8000:8000 --name bhoomiputhra bhoomiputhra:latest

# View logs
docker logs -f bhoomiputhra

# Stop container
docker stop bhoomiputhra

# Remove container
docker rm bhoomiputhra
```

---

## 🔧 Troubleshooting Commands

### Permission Issues
```bash
# Fix ownership
sudo chown -R www-data:www-data /path/to/project

# Fix permissions
sudo chmod -R 755 /path/to/project
sudo chmod -R 775 /path/to/project/media
sudo chmod -R 775 /path/to/project/logs
```

### Clear Cache
```bash
# Clear Django cache
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()

# Clear Redis cache (if using Redis)
redis-cli FLUSHALL
```

### Reset Database
```bash
# WARNING: This will delete all data!
python manage.py flush

# Or drop and recreate
python manage.py dbshell
DROP DATABASE bhoomi_puthra_db;
CREATE DATABASE bhoomi_puthra_db;
\q
python manage.py migrate
```

---

## 📝 Quick Checks

### Health Check
```bash
# Check if server is running
curl http://localhost:8000/health/

# Check static files
curl http://localhost:8000/static/css/style.css

# Check HTTPS redirect
curl -I http://yourdomain.com
```

### Security Headers
```bash
# Check security headers
curl -I https://yourdomain.com | grep -E "X-Frame-Options|X-Content-Type-Options|Strict-Transport-Security"
```

---

**Quick Reference Version**: 1.0  
**Last Updated**: February 12, 2026
