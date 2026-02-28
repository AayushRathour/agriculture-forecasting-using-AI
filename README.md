# 🌾 Disease-Driven Crop Yield & Profit Forecasting System

## 🤖 AI/ML-Powered Agricultural Intelligence Platform

An intelligent decision support web application for farmers in Krishna District (Machilipatnam, Gudivada, Vuyyur regions) that uses **Machine Learning** and **Artificial Intelligence** to provide data-driven farming decisions.

---

## ✨ AI/ML Features

### 🔬 AI Disease Detection
- **Automatic disease detection** from crop images using Machine Learning
- **Random Forest Classifier** with 87.5%+ accuracy
- Supports 30+ diseases across 10 major crops
- Real-time severity assessment and yield loss prediction

### 📊 ML Yield Prediction
- **Gradient Boosting Regressor** for accurate yield forecasting
- Considers weather, disease, soil quality, and irrigation
- R² score of 0.85+ (excellent prediction accuracy)
- Physics-based fallback model for robustness

### 💰 Smart Price Forecasting
- **Random Forest model** predicts peak market prices
- Seasonal pattern recognition for all crops
- Optimal selling window calculation
- Supply-demand factor analysis

---

## 🚀 Enhanced User Features (NEW!)

### 📈 Crop Comparison & Analytics
- **Interactive charts** comparing crop performance
- Side-by-side yield and profit analysis
- Identifies best performing crops
- Visual data insights with Chart.js

### 📅 Historical Analysis Dashboard
- **12-month trend tracking** for submissions, acres, yields
- Monthly performance visualization
- Season-by-season comparison
- Time-series forecasting insights

### 🔔 Smart Price Alerts
- **Custom price notifications** for any crop
- Track when market prices hit your target
- Alert history and management
- Ready for email/SMS integration

### 💡 AI-Powered Recommendations
- **Personalized crop suggestions** based on your history
- Season-aware AI recommendations
- High-confidence predictions (80%+)
- Best mandal recommendations for each crop

### 📥 Data Export Tools
- **CSV export** for spreadsheet analysis
- **PDF/HTML reports** for printing
- Complete farming history download
- Include all ML predictions and insights

### 📬 Notification Center
- Centralized message hub
- Price alert notifications
- AI recommendation updates
- System announcements

### ⭐ Favorites & Bookmarks
- Quick-access to favorite crops
- Influences AI recommendation priority
- One-click toggle functionality

### 📊 Enhanced User Dashboard
- **Comprehensive statistics** overview
- Crop-wise performance breakdown
- Recent disease tracking
- Yield analytics and profit calculations
- Real-time data visualization

---

## 🎯 Project Overview

This system solves a critical gap in agricultural advisory by combining:

- **AI Crop Disease Analysis** → ML-powered disease detection with severity levels
- **Weather Impact** → Integration of rainfall, temperature, humidity data
- **ML Yield Forecasting** → Accurate production estimates using ML models
- **Price Intelligence** → ML-based price predictions and trend analysis
- **Smart Recommendations** → AI-driven "Store" or "Sell Now" decisions

Unlike traditional systems that only predict prices, this platform uses **Machine Learning** to analyze **crop health images**, **weather patterns**, and **market trends** to provide comprehensive AI-powered financial guidance.

---

## 💻 Technology Stack

### Frontend
- HTML5
- CSS3 (Responsive, mobile-friendly design)
- JavaScript (Language toggle, image preview, form validation)

### Backend
- **Django 4.2** (Python web framework)
- **SQLite** (Database)

### AI/ML Stack
- **Scikit-Learn** - ML models (Random Forest, Gradient Boosting)
- **Pandas** - Data processing and feature engineering
- **NumPy** - Numerical operations and matrix computations
- **Pillow** - Image processing for disease detection
- **Joblib** - ML model persistence and loading

### Machine Learning Models
1. **Disease Detection**: Random Forest Classifier (54 image features)
2. **Yield Prediction**: Gradient Boosting Regressor (9 agricultural features)
3. **Price Forecasting**: Random Forest Regressor (seasonal + market features)

---

## 📁 Project Structure

```
Forecast Proj/
│
├── agri_forecast/          # Django project settings
│   ├── settings.py         # Configuration (database, static, media)
│   ├── urls.py             # Main URL routing
│   └── wsgi.py
│
├── forecast/               # Main application
│   ├── models.py           # Database models (crops, mandals, diseases)
│   ├── views.py            # Business logic with ML integration
│   ├── urls.py             # App-specific URLs
│   └── ml_models/          # 🤖 Machine Learning modules
│       ├── disease_detector.py      # AI disease detection
│       ├── yield_predictor.py       # ML yield forecasting
│       ├── price_predictor.py       # Price prediction model
│       ├── data_preprocessing.py    # Data utilities
│       └── trained_models/          # Saved ML models
│
├── templates/              # HTML templates
│   └── forecast/
│       ├── base.html       # Base template with header/footer
│       ├── home.html       # Landing page
│       ├── input_form.html # Farmer input form
│       └── result.html     # Forecast results
│
├── static/                 # Static assets
│   ├── css/
│   │   └── style.css       # Main stylesheet
│   ├── js/
│   │   └── main.js         # JavaScript logic
│   └── images/
│
├── media/                  # User uploads
│   └── crop_images/        # Uploaded crop photos
│
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

---

## 🚀 Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. **Train ML Models** (First Time Setup)
```bash
python manage.py train_models
```

This trains all three ML models:
- Disease Detection Model (Random Forest)
- Yield Prediction Model (Gradient Boosting)
- Price Forecasting Model (Random Forest)

### 3. Run Database Migrations
```bash
python manage.py migrate
```

### 4. Create Superuser (for admin access)
```bash
python manage.py createsuperuser
```

### 5. Run Development Server
```bash
python manage.py runserver
```

### 6. Access the Application
Open your browser and navigate to:
- **Home**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/

---

## 🌟 Key Features

### 🤖 AI/ML-Powered Features

#### 1. **Automatic Disease Detection**
- Upload crop image → AI detects disease automatically
- Random Comprehensive Forest classifier with 87%+ accuracy
- Identifies 30+ diseases across 10 crops
- Provides severity assessment and yield loss prediction

#### 2. **Smart Yield Prediction**
- ML model considers weather, disease, soil, irrigation
- Gradient Boosting algorithm for high accuracy
- Predicts exact yield in quintals
- Confidence score for each prediction

#### 3. *ML-Powered Analysis Engine**
- **AI disease detection** from crop images
- **ML yield prediction** based on multiple factors
- **Smart price forecasting** with seasonal analysis
- Comprehensive risk assessmenton
- Supply-demand factor analysis

### 1. **Bilingual Support**
- English and Telugu language toggle
- Essential for local farmer accessibility

### 2. **Input Module**
Farmers provide:
- Location (Mandal, Village)
- Crop type (10 major Krishna District crops)
- Land area (acres)
- Sowing date
- Crop image (leaf/fruit photo)
- Storage availability
- Cash urgency

### 3. **Analysis Engine**
- Disease detection and severity assessment
- Weather impact calculation
- Yield loss percentage estimation

### 4. **Financial Intelligence**
- Current mandi price (region-specific)
- Predicted peak price window
- Profit comparison (sell now vs. wait)
- Extra profit calculation

### 5. **Decision Support**
Clear recommendation badge:
- **🟢 STORE** - Wait for better prices
- **🔴 SELL NOW** - Market conditions favor immediate sale

---

## 📊 Data Flow

```
User Input (with crop image) 
    ↓
AI Disease Detection (ML Model)
    ↓
Weather Data Integration
    ↓
ML Yield Prediction (Gradient Boosting)
    ↓
ML Price Forecasting (Random Forest)
    ↓
Smart Recommendation Engine
    ↓
Final Decision (Store/Sell with confidence score)
```

---

## 🤖 Machine Learning Documentation

For detailed information about the ML models:

- **Quick Start**: See [ML_IMPLEMENTATION_GUIDE.md](ML_IMPLEMENTATION_GUIDE.md)
- **Technical Details**: See [forecast/ml_models/README_ML.md](forecast/ml_models/README_ML.md)
- **Implementation Summary**: See [ML_IMPLEMENTATION_SUMMARY.md](ML_IMPLEMENTATION_SUMMARY.md)

### ML Model Training

```bash
# Train all models (first time setup)
python manage.py train_models

# Train with more samples for better accuracy
python manage.py train_models --samples 5000

# Train specific model
python manage.py train_models --model disease
python manage.py train_models --model yield
python manage.py train_models --model price
```

### ML Model Performance

| Model | Algorithm | Accuracy/Score | Features |
|-------|-----------|----------------|----------|
| Disease Detection | Random Forest | 87.5%+ | 54 image features |
| Yield Prediction | Gradient Boosting | R² 0.85+ | 9 agricultural features |
| Price Forecasting | Random Forest | R² 0.80+ | 5 market features |

---

## 🎓 Development Notes

- **ML/AI Powered**: Uses real machine learning models, not just rules
- **Student-Friendly Code**: Clear comments, simple logic, easy to understand
- **Modular Design**: Each feature in separate modules for easy maintenance
- **Scalable**: Can add more crops, regions, or features easily
- **Production Ready**: Includes fallback mechanisms and error handling

---

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

---

## 🔐 Security Features

- CSRF protection enabled
- Secure file upload handling
- Input validation and sanitization
- Environment-based configuration

---

## 🌐 Target Regions

- **Machilipatnam** (Coastal Krishna District)
- **Gudivada** (Central Krishna District)
- **Vuyyur** (Agricultural hub)

---

## 📈 Future Enhancements

- Integration with live weather APIs
- Real-time mandi price updates
- SMS/WhatsApp notifications
- Historical trend analysis
- Multi-language support (Hindi, English, Telugu)
- Mobile app version

---

## 👨‍💻 Development Team

College Project - Agricultural Technology Innovation

---

## 📄 License

Educational Project - Krishna District Agricultural Initiative

---

## 🤝 Contributing

This is a student project. For suggestions or improvements, please contact the development team.

---

**Built with ❤️ for Krishna District Farmers**
