# 🌾 Disease-Driven Crop Yield & Profit Forecasting System

An intelligent decision support web application for farmers in Krishna District (Machilipatnam, Gudivada, Vuyyur regions) that integrates crop health analysis, weather impact, yield prediction, and market intelligence to provide data-driven selling recommendations.

---

## 🎯 Project Overview

This system solves a critical gap in agricultural advisory by combining:

- **Crop Disease Analysis** → Real-time health assessment with severity levels
- **Weather Impact** → Integration of rainfall, temperature, humidity data
- **Yield Forecasting** → Accurate production estimates considering all factors
- **Market Intelligence** → Live mandi prices and future price predictions
- **Smart Recommendations** → Clear "Store" or "Sell Now" decisions

Unlike traditional systems that only predict prices, this platform considers **real-time crop health** and **weather conditions** to provide comprehensive financial guidance.

---

## 💻 Technology Stack

### Frontend
- HTML5
- CSS3 (Responsive, mobile-friendly design)
- JavaScript (Language toggle, image preview, form validation)

### Backend
- **Django 4.2** (Python web framework)
- **SQLite** (Database)

### Data & ML
- **Pandas** - Data processing
- **NumPy** - Numerical operations
- **Scikit-Learn** - Machine learning models
- **Pillow** - Image processing

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
│   ├── views.py            # Business logic
│   ├── urls.py             # App-specific URLs
│   └── ml_models/          # Machine learning modules
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

### 2. Run Database Migrations
```bash
python manage.py migrate
```

### 3. Create Superuser (for admin access)
```bash
python manage.py createsuperuser
```

### 4. Run Development Server
```bash
python manage.py runserver
```

### 5. Access the Application
Open your browser and navigate to:
- **Home**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/

---

## 🌟 Key Features

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
User Input → Disease Analysis → Weather Integration → Yield Prediction
                                                              ↓
                                           Market Price Fetching
                                                              ↓
                                     Profit Calculation & Comparison
                                                              ↓
                                     Final Recommendation (Store/Sell)
```

---

## 🎓 Development Notes

- **Student-Friendly Code**: Clear comments, simple logic, easy to understand
- **Modular Design**: Each feature in separate modules for easy maintenance
- **Scalable**: Can add more crops, regions, or features easily
- **No Virtual Environment Required**: Direct installation as per project requirements

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
