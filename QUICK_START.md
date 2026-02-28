# Quick Setup Guide - Bhoomi Puthra Agricultural Forecast

## ⚡ 5-Minute Quick Start

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Train ML Models (First Time Only)
```bash
python manage.py train_models
```
This trains the AI/ML models for:
- Disease Detection (from crop images)
- Yield Prediction
- Price Forecasting

### Step 3: Setup Database
```bash
python manage.py migrate
```

### Step 4: Create Admin Account
```bash
python manage.py setup_admin
```
Default credentials:
- Username: `admin`
- Password: `admin123`

### Step 5: Run Server
```bash
python manage.py runserver
```

### Step 6: Access Application
Open browser: http://localhost:8000/

---

## 🤖 ML Features Available

✅ **AI Disease Detection** - Automatic from crop images  
✅ **ML Yield Prediction** - Based on weather + disease + soil  
✅ **Smart Price Forecasting** - Seasonal patterns + market analysis  

See `ML_IMPLEMENTATION_GUIDE.md` for detailed ML documentation.

---

## 🎯 What's Available Now

### For Farmers
1. **Register/Login**: Create account at http://localhost:8000/register/
2. **Submit Crop Data**: Go to http://localhost:8000/farmer-input/
3. **View Predictions**: See results with selling recommendations
4. **Track History**: Check your profile for past submissions

### 🚀 NEW: Enhanced User Features (AI/ML Powered)
1. **Crop Comparison**: http://localhost:8000/crop-comparison/
   - Compare performance across all your crops
   - Interactive charts for yields and profits
   
2. **Historical Analysis**: http://localhost:8000/historical-analysis/
   - Track farming trends over 12 months
   - Monthly submissions, acres, and yield charts
   
3. **Price Alerts**: http://localhost:8000/price-alerts/
   - Set target prices for crops
   - Get notified when prices reach your target
   
4. **AI Recommendations**: http://localhost:8000/recommendations/
   - Get smart crop suggestions based on your history
   - Season-aware AI recommendations
   
5. **Data Export**: http://localhost:8000/export/csv/ or /export/pdf/
   - Download your farming data
   - CSV for Excel, PDF for reports
   
6. **Notifications**: http://localhost:8000/notifications/
   - View all system messages
   - Price alerts and recommendations

### For Admins
1. **Django Admin**: http://localhost:8000/admin/
2. **Custom Dashboard**: http://localhost:8000/af-admin/
3. **Data Analytics**: http://localhost:8000/data-analytics/
4. **Notification Creator**: http://localhost:8000/af-admin/notifications/create/
   - Send notifications to all users or specific groups
   - Bulk messaging capability
   - Multiple notification types (price alerts, recommendations, weather updates, system messages)
5. **Price Alerts Management**: http://localhost:8000/price-alerts/ (Admin only)

---

## 📊 Current Data

✅ **2,322 Weather Records** (2024-2026)
- Machilipatnam, Gudivada, Vuyyur

✅ **60 Market Prices** (2023)
- Paddy, Turmeric, Chillies, Sugarcane, Banana

---

## 🛠️ Useful Commands

### Add Sample Farmers
```bash
python manage.py populate_sample_data --farmers 20
```

### Verify Database
```bash
python verify_data.py
```

### Run Tests
```bash
python manage.py test
```

### Import Excel Data
```bash
python manage.py import_data --file "EPICS DATA.xlsx"
```

---

## 🔐 Test Accounts

### Admin Account
- URL: http://localhost:8000/admin/
- Username: `admin`
- Password: `admin123`

### Create Regular User
Register at: http://localhost:8000/register/

---

## ✅ All Systems Ready

- ✅ Database configured
- ✅ Models optimized with indexes
- ✅ Security enhanced
- ✅ Logging configured
- ✅ Tests passing (9/9)
- ✅ No errors found

---

## 📖 Full Documentation

See `DOCUMENTATION.md` for complete guide.
See `IMPROVEMENTS_SUMMARY.md` for all enhancements.

---

**You're all set! The project is fully working and ready to use! 🚀**
