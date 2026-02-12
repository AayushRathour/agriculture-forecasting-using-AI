# 🗄️ DATABASE SCHEMA VISUALIZATION

## Complete Database Structure for Crop Forecasting System

```
┌─────────────────────────────────────────────────────────────────┐
│                        FORECAST_FARMER                          │
│  Primary Input Table - Stores Farmer & Crop Information        │
├─────────────────────────────────────────────────────────────────┤
│ PK  id                    BigAutoField                          │
│     mandal                CharField (machilipatnam/gudivada/...)│
│     village               CharField                             │
│     crop                  CharField (paddy/mango/chillies/...)  │
│     acres                 FloatField (min: 0.1)                 │
│     sowing_date           DateField                             │
│     cold_storage          BooleanField                          │
│     urgent_cash           BooleanField                          │
│     created_at            DateTimeField (auto)                  │
│     updated_at            DateTimeField (auto)                  │
└─────────────────────────────────────────────────────────────────┘
            │                                   ▲
            │ One-to-Many                       │ One-to-One
            ▼                                   │
┌─────────────────────────────────────────────────────────────────┐
│                   FORECAST_DISEASERECORD                        │
│  Crop Health Analysis - Multiple Diseases per Farmer           │
├─────────────────────────────────────────────────────────────────┤
│ PK  id                    BigAutoField                          │
│ FK  farmer_id             → forecast_farmer.id (CASCADE)        │
│     disease_name          CharField                             │
│     severity              CharField (low/medium/high)           │
│     image                 ImageField (crop_images/YYYY/MM/DD/)  │
│     yield_loss_percentage FloatField (0-100%)                   │
│     detection_date        DateTimeField (auto)                  │
│     notes                 TextField                             │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                  FORECAST_PREDICTIONRESULT                      │
│  Final Output - Complete Forecasting Results (1:1 with Farmer) │
├─────────────────────────────────────────────────────────────────┤
│ PK  id                         BigAutoField                     │
│ FK  farmer_id                  → forecast_farmer.id (CASCADE)   │
│                                  UNIQUE (OneToOne)              │
│                                                                 │
│     YIELD PREDICTION:                                           │
│     predicted_yield            FloatField (quintals)            │
│     yield_reduction_percentage FloatField (0-100%)              │
│                                                                 │
│     CURRENT MARKET:                                             │
│     current_market_price       FloatField (₹ per quintal)       │
│     total_current_value        FloatField (₹)                   │
│                                                                 │
│     FUTURE PREDICTION:                                          │
│     predicted_peak_price       FloatField (₹ per quintal)       │
│     peak_price_date            DateField                        │
│     total_future_value         FloatField (₹)                   │
│                                                                 │
│     PROFIT ANALYSIS:                                            │
│     profit_delta               FloatField (₹)                   │
│                                                                 │
│     RECOMMENDATION:                                             │
│     recommendation             CharField (store/sell)           │
│     recommendation_reason      TextField                        │
│     confidence_score           FloatField (0-100%)              │
│                                                                 │
│     generated_at               DateTimeField (auto)             │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                    FORECAST_WEATHERDATA                         │
│  Weather Information - Independent, Filtered by Mandal         │
├─────────────────────────────────────────────────────────────────┤
│ PK  id           BigAutoField                                   │
│     mandal       CharField (machilipatnam/gudivada/vuyyur)      │
│     rainfall     FloatField (mm, min: 0)                        │
│     temperature  FloatField (°C)                                │
│     humidity     FloatField (%, 0-100)                          │
│     date         DateField                                      │
│                                                                 │
│ UNIQUE INDEX: (mandal, date) - One record per mandal per day   │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                    FORECAST_MARKETPRICE                         │
│  Market Prices - Independent, Filtered by Crop & Region        │
├─────────────────────────────────────────────────────────────────┤
│ PK  id                BigAutoField                              │
│     crop              CharField (paddy/mango/chillies/...)      │
│     region            CharField (Vijayawada/Guntur/...)         │
│     price_per_quintal FloatField (₹, min: 0)                    │
│     date              DateField                                 │
│     is_peak_season    BooleanField                              │
│                                                                 │
│ UNIQUE INDEX: (crop, region, date) - One price per combo/day   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Relationship Types

### 1️⃣ **One-to-Many** (Farmer → DiseaseRecord)
- One Farmer can have **multiple** disease records
- Each DiseaseRecord belongs to **one** Farmer
- Cascade delete: If Farmer deleted, all related diseases deleted

**Example:**
```
Farmer #1 (Paddy, 5 acres)
  ├── Disease #1: Rice Blast (Medium)
  ├── Disease #2: Brown Spot (Low)
  └── Disease #3: Sheath Blight (High)
```

### 2️⃣ **One-to-One** (Farmer ↔ PredictionResult)
- One Farmer has **exactly one** prediction result
- Each PredictionResult belongs to **one** Farmer
- Unique constraint enforced

**Example:**
```
Farmer #1 ←→ PredictionResult #1
```

### 3️⃣ **Independent Tables** (WeatherData, MarketPrice)
- No direct foreign key relationships
- Filtered by attributes (mandal, crop, region)
- Used for lookups during prediction

---

## 🔄 Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INPUT STAGE                            │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌──────────────────────┐
              │   FARMER Record      │
              │  (Location + Crop)   │
              └──────────────────────┘
                          │
                          ▼
              ┌──────────────────────┐
              │  DISEASERECORD       │
              │  (Image + Severity)  │
              └──────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   ANALYSIS STAGE                                │
└─────────────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
  ┌──────────┐    ┌──────────────┐   ┌─────────────┐
  │ WEATHER  │    │   DISEASE    │   │   MARKET    │
  │   DATA   │    │   SEVERITY   │   │   PRICE     │
  │(mandal)  │    │ (yield loss) │   │ (crop/region)│
  └──────────┘    └──────────────┘   └─────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          ▼
              ┌──────────────────────┐
              │   ML PREDICTION      │
              │   ALGORITHMS         │
              └──────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUT STAGE                                 │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌──────────────────────┐
              │ PREDICTIONRESULT     │
              │ - Yield Forecast     │
              │ - Profit Analysis    │
              │ - Store/Sell Badge   │
              └──────────────────────┘
```

---

## 🎯 Table Purposes

| Table | Purpose | Query Pattern |
|-------|---------|---------------|
| **Farmer** | Store farmer input | Insert on form submit |
| **DiseaseRecord** | Store disease analysis | Insert after image analysis |
| **WeatherData** | Provide weather context | Lookup by mandal + date range |
| **MarketPrice** | Provide price data | Lookup by crop + region + date |
| **PredictionResult** | Store final output | Insert/Update after prediction |

---

## 📏 Field Sizes & Constraints

### Character Fields:
- `mandal`: 50 chars (choice field)
- `village`: 100 chars
- `crop`: 50 chars (choice field)
- `disease_name`: 200 chars
- `severity`: 20 chars (choice field)
- `region`: 100 chars
- `recommendation`: 20 chars (choice field)

### Numeric Fields:
- `acres`: Float (min 0.1)
- `rainfall`: Float (min 0)
- `temperature`: Float (no limit)
- `humidity`: Float (0-100)
- `price_per_quintal`: Float (min 0)
- `yield_loss_percentage`: Float (0-100)
- `confidence_score`: Float (0-100)

### Date/Time Fields:
- `sowing_date`: Date
- `detection_date`: DateTime (auto)
- `date`: Date
- `peak_price_date`: Date (nullable)
- `created_at`, `updated_at`, `generated_at`: DateTime (auto)

### Boolean Fields:
- `cold_storage`: Boolean
- `urgent_cash`: Boolean
- `is_peak_season`: Boolean

### File Fields:
- `image`: ImageField (path: crop_images/YYYY/MM/DD/)

---

## 🔐 Indexes & Constraints

### Primary Keys:
- All tables: `id` (BigAutoField, auto-increment)

### Foreign Keys:
- `DiseaseRecord.farmer_id` → `Farmer.id` (CASCADE)
- `PredictionResult.farmer_id` → `Farmer.id` (CASCADE, UNIQUE)

### Unique Constraints:
- `WeatherData`: (mandal, date)
- `MarketPrice`: (crop, region, date)
- `PredictionResult`: farmer_id (OneToOne)

### Implicit Indexes:
- Foreign key columns
- Unique constraint columns
- Primary key columns

---

## 💾 Storage Considerations

### Image Storage:
- Path: `media/crop_images/YYYY/MM/DD/filename.jpg`
- Organized by upload date
- Requires MEDIA_ROOT configuration ✅

### Database Size Estimation:

**Per Farmer Record:** ~500 bytes
- 1000 farmers = ~0.5 MB

**Per Disease Record:** ~1 KB + image size
- 1000 diseases (avg 1MB images) = ~1 GB

**Per Weather Record:** ~100 bytes
- 365 days × 3 mandals = ~36 KB/year

**Per Market Price:** ~100 bytes
- 10 crops × 5 regions × 365 days = ~183 KB/year

**Per Prediction:** ~500 bytes
- 1000 predictions = ~0.5 MB

**Total (excluding images):** ~2 MB for 1000 farmers
**With images:** ~1 GB for 1000 farmers

---

## 🔍 Query Patterns

### Common Queries:

**Get farmer with all data:**
```python
farmer = Farmer.objects.select_related('prediction').prefetch_related('diseases').get(id=1)
```

**Get recent diseases:**
```python
recent = DiseaseRecord.objects.select_related('farmer').order_by('-detection_date')[:10]
```

**Get weather for a mandal:**
```python
weather = WeatherData.objects.filter(
    mandal='machilipatnam',
    date__gte=date.today() - timedelta(days=7)
)
```

**Get latest crop price:**
```python
price = MarketPrice.objects.filter(
    crop='paddy',
    region='Vijayawada'
).order_by('-date').first()
```

**Get all "STORE" recommendations:**
```python
stores = PredictionResult.objects.filter(
    recommendation='store',
    profit_delta__gte=10000
)
```

---

## ✅ Migration Status

**Migration File:** `forecast/migrations/0001_initial.py`
**Created:** February 12, 2026 at 13:43 IST
**Status:** ✅ Applied Successfully

**Tables Created:**
1. ✅ forecast_farmer
2. ✅ forecast_diseaserecord
3. ✅ forecast_weatherdata
4. ✅ forecast_marketprice
5. ✅ forecast_predictionresult

**Django Admin:** ✅ All models registered with custom interfaces

---

**Database is ready for data population and application logic!** 🚀
