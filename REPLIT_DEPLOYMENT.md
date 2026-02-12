# 🌾 Bhoomi Puthra - Replit Deployment Guide

## 📋 Complete Step-by-Step Guide to Deploy on Replit

---

## ✨ Why Replit?

- ✅ Free hosting with always-on option
- ✅ Built-in database (PostgreSQL available)
- ✅ Automatic HTTPS
- ✅ Easy environment variable management
- ✅ Zero configuration deployment
- ✅ Built-in code editor and terminal

---

## 🚀 Deployment Steps

### Step 1: Create Replit Account

1. Go to [https://replit.com](https://replit.com)
2. Sign up for a free account (or log in if you have one)
3. Verify your email address

### Step 2: Create New Repl

1. Click **"+ Create Repl"** button
2. Choose **"Import from GitHub"** tab
3. **OR** Choose **"Upload project files"** if you don't use GitHub

#### Option A: Import from GitHub
1. If your project is on GitHub, paste the repository URL
2. Replit will automatically detect it's a Python project
3. Click **"Import from GitHub"**

#### Option B: Upload Files
1. Select **"Python"** as the template
2. Name your Repl: **"bhoomi-puthra"**
3. Click **"Create Repl"**
4. Upload all project files using the Files panel (drag & drop)

### Step 3: Configure Environment Variables (Secrets)

1. Click on **🔒 Secrets** (lock icon) in the left sidebar
2. Add the following secrets:

```
SECRET_KEY = [Generate new key - see instructions below]
DEBUG = False
ADMIN_SECRET_KEY = AGRI2026
```

**To generate a new SECRET_KEY:**
- Open the Shell tab in Replit
- Run: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- Copy the output and paste it as SECRET_KEY value

### Step 4: Install Dependencies

In the Replit Shell, run:

```bash
pip install -r requirements.txt
```

This will install:
- Django 4.2
- Pillow (image processing)
- gunicorn (production server)
- whitenoise (static files)
- pandas, numpy, scikit-learn (data processing)

### Step 5: Setup Database

Run these commands in the Shell:

```bash
# Run migrations
python manage.py migrate

# Create superuser (for admin access)
python manage.py createsuperuser
# Enter username, email, and password when prompted

# Collect static files
python manage.py collectstatic --noinput

# Load initial data (if you have fixtures)
# python manage.py loaddata initial_data.json
```

### Step 6: Run the Application

Click the **"▶ Run"** button at the top of Replit

Or manually in Shell:
```bash
python manage.py runserver 0.0.0.0:8000
```

The application will start and Replit will provide you a URL like:
```
https://bhoomi-puthra.yourusername.repl.co
```

### Step 7: Verify Deployment

Visit your Repl URL and check:
- ✅ Home page loads
- ✅ Can navigate to farmer input form
- ✅ Static files (CSS/JS) are loading correctly
- ✅ Can register/login
- ✅ Admin panel works at `/af-admin/`

---

## 🔧 Replit Configuration Files

The following files have been created for Replit:

### 1. `.replit` - Main Configuration
Tells Replit how to run your application and configure the environment.

### 2. `replit.nix` - System Dependencies
Specifies Python version and system packages needed.

### 3. `runtime.txt` - Python Version
Specifies Python 3.10.12 for consistency.

### 4. `Procfile` - Process Configuration
Used by Replit's deployment system for production mode.

---

## ⚙️ Replit-Specific Configuration

### Automatic ALLOWED_HOSTS
The settings.py has been updated to automatically detect Replit domains:
```python
# Automatically adds:
# your-repl.username.repl.co
```

### WhiteNoise for Static Files
Added WhiteNoise middleware to serve static files without needing a separate web server.

### SSL/HTTPS Settings
Disabled `SECURE_SSL_REDIRECT` for Replit as it handles HTTPS automatically.

---

## 🗄️ Database Options on Replit

### Option 1: SQLite (Default - Included)
- ✅ Already configured
- ✅ No setup required
- ✅ Good for small to medium traffic
- ⚠️ Data persists but can be lost if repl is deleted

### Option 2: Replit Database (PostgreSQL)
For production-grade database:

1. Enable Replit DB in your repl settings
2. Install PostgreSQL adapter:
```bash
pip install psycopg2-binary dj-database-url
```

3. Update settings.py:
```python
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}
```

4. Add to Secrets:
```
DATABASE_URL = [Replit will provide this]
```

---

## 📊 Managing Your Repl

### Keep Your Repl Always Running

**Free Tier:**
- Repl sleeps after inactivity
- Wakes up when someone visits

**Paid Plan (Hacker/Pro):**
1. Go to your repl
2. Click "Always On" toggle
3. Your repl will run 24/7

### Updating Your Application

1. Edit files in Replit's code editor
2. Changes are auto-saved
3. Click "Stop" then "Run" to restart with changes

### Viewing Logs

1. Click on "Console" tab
2. All Django logs appear here
3. Error logs are in `logs/django_errors.log`

### Backing Up Data

```bash
# Export data
python manage.py dumpdata > backup.json

# Download backup.json from Files panel
```

---

## 🔒 Security Best Practices for Replit

### 1. Environment Variables
✅ Always use Secrets for sensitive data
❌ Never hardcode passwords/keys in code

### 2. Secret Key
✅ Generate unique SECRET_KEY for production
❌ Don't use the default Django secret key

### 3. Debug Mode
✅ Set DEBUG=False in production
❌ Never run with DEBUG=True in production

### 4. Admin Access
- Use strong passwords for admin accounts
- Change the admin secret key from default
- Regularly review admin users

---

## 📱 Custom Domain (Optional)

### With Replit Paid Plan:
1. Go to your repl settings
2. Click "Domains"
3. Add your custom domain
4. Update DNS records as instructed
5. Add your domain to ALLOWED_HOSTS in Secrets

---

## 🐛 Troubleshooting

### Issue: Static files not loading
**Solution:**
```bash
python manage.py collectstatic --clear --noinput
```

### Issue: Database errors
**Solution:**
```bash
# Re-run migrations
python manage.py migrate --run-syncdb
```

### Issue: Module not found
**Solution:**
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### Issue: 502 Bad Gateway
**Solution:**
- Check if the app is running on port 8000
- Restart the repl
- Check Console for error messages

### Issue: CSRF errors
**Solution:**
Add to Secrets:
```
CSRF_TRUSTED_ORIGINS = https://your-repl.username.repl.co
```

---

## 📈 Performance Tips

### 1. Enable Caching
Already configured with local memory cache for basic performance.

### 2. Optimize Static Files
WhiteNoise automatically compresses and caches static files.

### 3. Database Queries
Your models are already optimized with proper indexing.

### 4. Use Always On (Paid)
Prevents cold starts and keeps your repl responsive.

---

## 💰 Replit Pricing (as of 2026)

### Free Tier
- ✅ Unlimited public repls
- ✅ 500MB storage
- ✅ Basic compute
- ⚠️ Sleeps after inactivity
- ⚠️ Shared resources

### Hacker Plan (~$7/month)
- ✅ Always On repls
- ✅ More storage (5GB)
- ✅ Private repls
- ✅ Faster compute
- ✅ Custom domains

### Pro Plan (~$20/month)
- ✅ Everything in Hacker
- ✅ Even more resources
- ✅ Priority support
- ✅ Team collaboration

---

## 🎯 Post-Deployment Checklist

After deploying, verify:

- [ ] Application loads at Replit URL
- [ ] Static files (CSS/JS/images) load correctly
- [ ] Can register new user
- [ ] Can login/logout
- [ ] Farmer input form works
- [ ] Results page displays correctly
- [ ] Admin panel accessible at `/af-admin/`
- [ ] Data Analytics page shows data
- [ ] Error pages work (test 404)
- [ ] All tests pass: `python manage.py test`

---

## 🔄 Continuous Updates

### Method 1: Edit in Replit
1. Edit files directly in Replit
2. Stop and restart the repl

### Method 2: Git Integration
1. Connect Repl to GitHub repository
2. Pull latest changes
3. Restart repl

---

## 📞 Support Resources

- **Replit Docs:** https://docs.replit.com
- **Replit Community:** https://ask.replit.com
- **Django Docs:** https://docs.djangoproject.com
- **Your Django Logs:** Check Console tab

---

## 🎉 Your Replit Deployment URL

Once deployed, your application will be available at:

```
https://bhoomi-puthra-yourusername.repl.co
```

**Share this URL with:**
- Farmers in Krishna District
- Agricultural officers
- Development team
- Stakeholders

---

## 🌟 Next Steps After Deployment

1. **Test thoroughly** - Try all features
2. **Load sample data** - Use the data import scripts
3. **Create admin account** - For managing the system
4. **Share the URL** - With your users
5. **Monitor usage** - Check logs regularly
6. **Gather feedback** - From farmers and improve

---

**Deployment Type:** Replit Cloud Platform  
**Last Updated:** February 13, 2026  
**Version:** 1.0.0  
**Project:** Bhoomi Puthra - Agricultural Forecasting System

---

## 🎊 Congratulations!

Your Bhoomi Puthra application is now live and accessible to farmers across Krishna District! 🌾

**Live URL:** `https://[your-repl-name].[your-username].repl.co`
