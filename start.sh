#!/bin/bash

# Replit Startup Script for Django App

echo "🚀 Starting Bhoomi Puthra - Crop Forecasting System"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# Create superuser if needed (for first run)
echo "👤 Checking for superuser..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superuser created: username=admin, password=admin123')
else:
    print('✅ Superuser already exists')
EOF

# Collect static files (if needed for production)
# python manage.py collectstatic --noinput

echo "✅ Setup complete!"
echo "🌐 Starting Django development server..."
python manage.py runserver 0.0.0.0:8000
