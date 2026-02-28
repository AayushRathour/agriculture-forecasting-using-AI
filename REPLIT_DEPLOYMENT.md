# 🌾 Bhoomi Puthra - AI-Powered Crop Forecasting System

## 🚀 Quick Deploy to Replit

### Automated Setup
1. Fork/Import this repository to Replit
2. Click "Run" button - The system will automatically:
   - Install all dependencies
   - Run database migrations
   - Create admin superuser
   - Start the Django server

### Default Admin Credentials
- **Username:** `admin`
- **Password:** `admin123`
- **Admin Panel:** `http://your-repl.repl.co/af-admin/login/`

⚠️ **Change these credentials immediately after first login!**

---

## 📋 Manual Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Database Migrations
```bash
python manage.py migrate
```

### 3. Create Superuser (if not auto-created)
```bash
python manage.py createsuperuser
```

### 4. Populate Sample Data (Optional)
```bash
python manage.py populate_sample_data
```

### 5. Start Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```

---

## 🌐 Access URLs

### User Pages
- **Home:** `/`
- **Login:** `/login/`
- **Register:** `/register/`
- **Farmer Input:** `/farmer-input/`
- **User Profile:** `/profile/`
- **Crop Comparison:** `/crop-comparison/`
- **Historical Analysis:** `/historical-analysis/`
- **Recommendations:** `/recommendations/`
- **Notifications:** `/notifications/`
- **Data Analytics:** `/data-analytics/` (Staff only)

### Admin Panel
- **Dashboard:** `/af-admin/`
- **Login:** `/af-admin/login/`
- **Users Management:** `/af-admin/users/`
- **Farmers Data:** `/af-admin/farmers/`
- **Weather Data:** `/af-admin/weather/`
- **Market Prices:** `/af-admin/prices/`
- **System Logs:** `/af-admin/logs/`
- **Notifications Creator:** `/af-admin/notifications/create/`

---

## 🔧 Environment Variables (Optional)

Create a `.env` file or set these in Replit Secrets:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,your-repl-domain.repl.co
```

---

## 📦 Features

### For Farmers/Users
✅ AI-powered crop yield prediction  
✅ Disease detection system  
✅ Market price forecasting  
✅ Crop performance comparison  
✅ Historical trend analysis  
✅ Personalized recommendations  
✅ Price alerts & notifications  
✅ Data export (CSV/PDF)  

### For Administrators
✅ User management system  
✅ Farmer data oversight  
✅ Weather data management  
✅ Market price administration  
✅ Bulk notification system  
✅ System logs viewer  
✅ Data analytics dashboard  
✅ CSV exports for all data  

---

## 🛠️ Technology Stack

- **Backend:** Django 4.2.17
- **Database:** SQLite (default) / PostgreSQL (production)
- **Frontend:** Bootstrap 5.3, Chart.js
- **ML/AI:** scikit-learn, pandas, numpy
- **Authentication:** Django Auth System

---

## 📊 Database Models

1. **Farmer** - Crop submission records
2. **DiseaseRecord** - Disease detection data
3. **WeatherData** - Historical weather information
4. **MarketPrice** - Market price history
5. **PredictionResult** - ML prediction outputs
6. **PriceAlert** - Price notification settings
7. **FavoriteCrop** - User crop preferences
8. **Notification** - User notifications

---

## 🔐 Security Features

- User authentication & authorization
- Staff-only admin panel access
- CSRF protection on all forms
- User data isolation
- Secure password hashing
- Permission-based access control

---

## 📱 Responsive Design

The application is fully responsive and works on:
- 💻 Desktop browsers
- 📱 Mobile devices
- 📱 Tablets

---

## 🆘 Troubleshooting

### Server won't start
```bash
# Check for errors
python manage.py check

# Try running migrations again
python manage.py migrate
```

### Admin panel shows "Page not found"
Make sure you're accessing `/af-admin/` (not `/admin/`)

### Cannot login as admin
Reset superuser password:
```bash
python manage.py changepassword admin
```

### Missing dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

---

## 📚 Documentation

- `QUICK_START.md` - Getting started guide
- `PROJECT_SUMMARY.txt` - Project overview
- `ADMIN_PANEL_DOCUMENTATION.md` - Admin features
- `USER_FEATURES_GUIDE.md` - User features
- `ML_IMPLEMENTATION_GUIDE.md` - ML models

---

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the documentation files
3. Check Django logs: `logs/django.log`

---

## 📝 License

Educational/Personal Project - Krishna District, Andhra Pradesh, India

---

## 🌟 Credits

**Bhoomi Puthra** - AI-Powered Agricultural Forecasting System  
Developed for farmers in Krishna District to make data-driven decisions.

---

**Happy Farming! 🌾**
