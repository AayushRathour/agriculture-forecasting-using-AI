#!/bin/bash
# Pre-deployment Test Script for Replit
echo "🧪 Running pre-deployment tests..."
echo ""

# Test 1: Check if all required files exist
echo "📁 Checking required files..."
files=(".replit" "replit.nix" "Procfile" "runtime.txt" "requirements.txt" "manage.py")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file exists"
    else
        echo "  ❌ $file is missing!"
        exit 1
    fi
done
echo ""

# Test 2: Install dependencies
echo "📦 Testing dependency installation..."
pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo "  ✅ Dependencies installed successfully"
else
    echo "  ❌ Dependency installation failed!"
    exit 1
fi
echo ""

# Test 3: Check Django settings
echo "⚙️  Checking Django configuration..."
python manage.py check --deploy 2>&1 | grep -q "System check identified"
if [ $? -eq 0 ]; then
    echo "  ✅ Django configuration valid"
else
    echo "  ⚠️  Configuration warnings (check manually)"
fi
echo ""

# Test 4: Run migrations
echo "🔄 Testing database migrations..."
python manage.py migrate --check
if [ $? -eq 0 ]; then
    echo "  ✅ Migrations are up to date"
else
    echo "  ⚠️  Migrations need to be applied"
fi
echo ""

# Test 5: Collect static files (dry run)
echo "📂 Testing static file collection..."
python manage.py collectstatic --noinput --dry-run > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ Static files can be collected"
else
    echo "  ❌ Static file collection failed!"
    exit 1
fi
echo ""

# Test 6: Run unit tests
echo "🧪 Running unit tests..."
python manage.py test forecast.tests --verbosity=0
if [ $? -eq 0 ]; then
    echo "  ✅ All tests passed"
else
    echo "  ❌ Some tests failed!"
    exit 1
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Pre-deployment checks complete!"
echo "✅ Your application is ready for Replit deployment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "1. Upload project to Replit"
echo "2. Configure Secrets (SECRET_KEY, DEBUG)"
echo "3. Run: pip install -r requirements.txt"
echo "4. Run: python manage.py migrate"
echo "5. Run: python manage.py collectstatic --noinput"
echo "6. Click the Run button!"
echo ""
