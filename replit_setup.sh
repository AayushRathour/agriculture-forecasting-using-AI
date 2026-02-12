#!/bin/bash
# Replit Setup Script for Bhoomi Puthra

echo "🌾 Setting up Bhoomi Puthra on Replit..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating required directories..."
mkdir -p logs
mkdir -p media
mkdir -p staticfiles

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate

# Collect static files
echo "📂 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser (optional - can be done manually)
echo ""
echo "✅ Setup complete!"
echo ""
echo "⚠️  IMPORTANT: Configure the following in Replit Secrets:"
echo "    - SECRET_KEY (generate a new one)"
echo "    - DEBUG=False"
echo "    - ALLOWED_HOSTS (will be set automatically by Replit)"
echo ""
echo "🚀 Your application is ready to run!"
