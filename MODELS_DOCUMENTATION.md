# 📊 DATABASE MODELS DOCUMENTATION

## ✅ Models Successfully Created

All 5 models have been created, migrated, and registered in Django admin!

---

## 🗃️ Model Structure Overview

### 1️⃣ **Farmer Model** (Primary Input)

Stores farmer's basic information and crop details.

**Fields:**
- `mandal` - Choice field (Machilipatnam, Gudivada, Vuyyur)
- `village` - Village name (CharField)
- `crop` - Choice field (10 major Krishna District crops)
- `acres` - Land area (FloatField, min: 0.1)
- `sowing_date` - Date when crop was sown (DateField)
- `cold_storage` - Cold storage access (BooleanField)
- `urgent_cash` - Urgent cash need (BooleanField)
- `created_at`, `updated_at` - Auto timestamps

**10 Supported Crops:**
1. Paddy (Rice)
2. Mango
3. Chillies
4. Cotton
5. Turmeric
6. Sugarcane
7. Banana
8. Tomato
9. Okra (Bhendi)
10. Brinjal (Eggplant)

**Methods:**
- `crop_age_days()` - Calculate days since sowing

**Relationships:**
- One-to-Many with DiseaseRecord
- One-to-One with PredictionResult

---

### 2️⃣ **DiseaseRecord Model** (Crop Health)

Stores disease detection results for farmer's crop.

**Fields:**
- `farmer` - ForeignKey to Farmer (CASCADE)
- `disease_name` - Name of detected disease (CharField)
- `severity` - Choice field (Low, Medium, High)
- `image` - Crop image upload (ImageField)
- `yield_loss_percentage` - Estimated yield loss (FloatField, 0-100%)
- `detection_date` - Auto-generated timestamp (DateTimeField)
- `notes` - Additional observations (TextField)

**Image Upload Path:** `media/crop_images/YYYY/MM/DD/`

**Relationships:**
- Many-to-One with Farmer

---

### 3️⃣ **WeatherData Model** (Environmental Factors)

Stores weather data for each mandal.

**Fields:**
- `mandal` - Choice field (Machilipatnam, Gudivada, Vuyyur)
- `rainfall` - Rainfall in mm (FloatField, min: 0)
- `temperature` - Temperature in °C (FloatField)
- `humidity` - Humidity percentage (FloatField, 0-100%)
- `date` - Weather data date (DateField)

**Unique Constraint:** One record per mandal per day

**Usage:** Used to calculate weather impact on yield prediction

---

### 4️⃣ **MarketPrice Model** (Mandi Prices)

Stores current and historical market prices.

**Fields:**
- `crop` - Choice field (10 crops)
- `region` - Market/Mandi location (CharField)
- `price_per_quintal` - Price in ₹ (FloatField, min: 0)
- `date` - Price recording date (DateField)
- `is_peak_season` - Peak season flag (BooleanField)

**Unique Constraint:** One price per crop per region per day

**Usage:** Used for profit calculation and selling recommendations

---

### 5️⃣ **PredictionResult Model** (Final Output)

Stores complete forecasting results for a farmer.

**Fields:**

**Yield Prediction:**
- `farmer` - OneToOneField to Farmer (CASCADE)
- `predicted_yield` - Estimated production in quintals (FloatField)
- `yield_reduction_percentage` - Reduction due to disease/weather (FloatField, 0-100%)

**Current Market:**
- `current_market_price` - Current price per quintal (FloatField)
- `total_current_value` - Current total crop value (FloatField)

**Future Prediction:**
- `predicted_peak_price` - Expected peak price (FloatField)
- `peak_price_date` - Expected peak date (DateField)
- `total_future_value` - Potential value at peak (FloatField)

**Profit Analysis:**
- `profit_delta` - Extra profit by waiting (FloatField)

**Recommendation:**
- `recommendation` - Choice field (STORE or SELL NOW)
- `recommendation_reason` - Explanation (TextField)
- `confidence_score` - Prediction confidence (FloatField, 0-100%)

**Metadata:**
- `generated_at` - Auto timestamp (DateTimeField)

**Methods:**
- `profit_percentage()` - Calculate profit increase percentage

**Relationships:**
- One-to-One with Farmer

---

## 🔗 Relationships Diagram

```
Farmer (1) ←→ (1) PredictionResult
   ↓
   └── (Many) DiseaseRecord

WeatherData (Independent - filtered by mandal)
MarketPrice (Independent - filtered by crop)
```

---

## 🎨 Django Admin Features

All models are registered with **custom admin interfaces**:

### Farmer Admin:
- ✅ List view with icons for cold storage and urgent cash
- ✅ Filters: mandal, crop, storage, cash need
- ✅ Search: village, mandal, crop
- ✅ Organized fieldsets

### Disease Record Admin:
- ✅ Colored severity badges (Green/Orange/Red)
- ✅ Image preview in admin
- ✅ Filters: severity, date, crop
- ✅ Search: disease name, village

### Weather Data Admin:
- ✅ Formatted display (°C, mm, %)
- ✅ Filters: mandal, date
- ✅ Date hierarchy

### Market Price Admin:
- ✅ Formatted price display (₹)
- ✅ Peak season icons
- ✅ Filters: crop, region, season
- ✅ Date hierarchy

### Prediction Result Admin:
- ✅ Colored recommendation badges (🟢 STORE / 🔴 SELL NOW)
- ✅ Formatted profit display
- ✅ Profit percentage calculation
- ✅ Filters: recommendation, date
- ✅ Comprehensive fieldsets

---

## 📝 Database Schema

**Tables Created:**
1. `forecast_farmer`
2. `forecast_diseaserecord`
3. `forecast_weatherdata`
4. `forecast_marketprice`
5. `forecast_predictionresult`

**Indexes:**
- Primary keys on all tables
- Foreign keys (farmer references)
- Unique constraints (weather, market price)

---

## 🚀 Next Steps

### To Access Admin Panel:

1. **Create superuser:**
```bash
python manage.py createsuperuser
```

2. **Access admin:**
http://127.0.0.1:8000/admin/

3. **Add sample data:**
- Farmers
- Weather data
- Market prices
- Disease records
- Predictions

---

## 💡 Usage Example

### Creating a Farmer Record:
```python
from forecast.models import Farmer
from datetime import date

farmer = Farmer.objects.create(
    mandal='machilipatnam',
    village='Pedana',
    crop='paddy',
    acres=5.0,
    sowing_date=date(2026, 1, 15),
    cold_storage=True,
    urgent_cash=False
)
```

### Creating a Disease Record:
```python
from forecast.models import DiseaseRecord

disease = DiseaseRecord.objects.create(
    farmer=farmer,
    disease_name='Rice Blast',
    severity='medium',
    yield_loss_percentage=15.0,
    notes='Brown spots on leaves'
)
```

### Creating Weather Data:
```python
from forecast.models import WeatherData
from datetime import date

weather = WeatherData.objects.create(
    mandal='machilipatnam',
    rainfall=25.5,
    temperature=32.0,
    humidity=75.0,
    date=date.today()
)
```

### Creating Market Price:
```python
from forecast.models import MarketPrice
from datetime import date

price = MarketPrice.objects.create(
    crop='paddy',
    region='Vijayawada',
    price_per_quintal=2150.00,
    date=date.today(),
    is_peak_season=False
)
```

### Creating Prediction Result:
```python
from forecast.models import PredictionResult
from datetime import date, timedelta

prediction = PredictionResult.objects.create(
    farmer=farmer,
    predicted_yield=75.0,
    yield_reduction_percentage=15.0,
    current_market_price=2150.00,
    total_current_value=161250.00,
    predicted_peak_price=2500.00,
    peak_price_date=date.today() + timedelta(days=30),
    total_future_value=187500.00,
    profit_delta=26250.00,
    recommendation='store',
    recommendation_reason='Peak season expected in 30 days. 16.3% profit gain.',
    confidence_score=85.5
)
```

---

## 🔍 Querying Examples

### Get all farmers from Machilipatnam growing paddy:
```python
farmers = Farmer.objects.filter(
    mandal='machilipatnam',
    crop='paddy'
)
```

### Get diseases with high severity:
```python
severe_diseases = DiseaseRecord.objects.filter(
    severity='high'
)
```

### Get latest market price for a crop:
```python
latest_price = MarketPrice.objects.filter(
    crop='mango',
    region='Vijayawada'
).order_by('-date').first()
```

### Get all "STORE" recommendations:
```python
store_recommendations = PredictionResult.objects.filter(
    recommendation='store'
)
```

### Get farmer with their prediction:
```python
farmer = Farmer.objects.get(id=1)
prediction = farmer.prediction  # One-to-one relationship
```

### Get all diseases for a farmer:
```python
farmer = Farmer.objects.get(id=1)
diseases = farmer.diseases.all()  # Reverse relationship
```

---

## 📊 Field Validations

**Built-in Validations:**
- `acres` - Minimum 0.1
- `yield_loss_percentage` - Range 0-100%
- `humidity` - Range 0-100%
- `rainfall` - Minimum 0
- `price_per_quintal` - Minimum 0
- `confidence_score` - Range 0-100%

**Unique Constraints:**
- WeatherData: (mandal, date)
- MarketPrice: (crop, region, date)

---

## 🎯 Model Status

| Model | Status | Relationships | Admin |
|-------|--------|---------------|-------|
| Farmer | ✅ Ready | Primary | ✅ Configured |
| DiseaseRecord | ✅ Ready | → Farmer | ✅ Configured |
| WeatherData | ✅ Ready | Independent | ✅ Configured |
| MarketPrice | ✅ Ready | Independent | ✅ Configured |
| PredictionResult | ✅ Ready | ↔ Farmer | ✅ Configured |

**All migrations applied successfully!** ✅

---

## 📱 Model Features Summary

**Bilingual Support:**
- Field verbose names include Telugu translations
- Help text for farmer accessibility

**Student-Friendly:**
- Comprehensive comments
- Clear field names
- Helpful methods

**Professional:**
- Proper relationships
- Validations
- Admin customization
- Metadata fields

**Scalable:**
- Easy to extend
- Add more crops
- Add more regions
- Add more features

---

**Status:** ✅ **Models Complete - Ready for Step 3 (Input Form Implementation)**
