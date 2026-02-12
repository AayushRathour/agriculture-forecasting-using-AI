# 🎮 DJANGO MODELS - QUICK COMMAND REFERENCE

## Essential Django Commands

### 🔧 Database Management

```bash
# Create migrations (after model changes)
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migrations status
python manage.py showmigrations

# Check for issues
python manage.py check

# Create superuser for admin access
python manage.py createsuperuser
```

---

## 🔍 Django Shell Commands

Access Django shell to interact with models:

```bash
python manage.py shell
```

### Import Models
```python
from forecast.models import Farmer, DiseaseRecord, WeatherData, MarketPrice, PredictionResult
from datetime import date, timedelta
```

---

## 📝 CREATE Operations

### Create Farmer
```python
farmer = Farmer.objects.create(
    mandal='machilipatnam',
    village='Pedana',
    crop='paddy',
    acres=5.0,
    sowing_date=date(2026, 1, 15),
    cold_storage=True,
    urgent_cash=False
)
print(f"Created Farmer ID: {farmer.id}")
```

### Create Disease Record
```python
# Method 1: Direct creation
disease = DiseaseRecord.objects.create(
    farmer=farmer,
    disease_name='Rice Blast',
    severity='medium',
    yield_loss_percentage=15.0,
    notes='Brown spots on leaves, spreading rapidly'
)

# Method 2: Using farmer relationship
disease = farmer.diseases.create(
    disease_name='Brown Spot',
    severity='low',
    yield_loss_percentage=5.0
)
```

### Create Weather Data
```python
weather = WeatherData.objects.create(
    mandal='machilipatnam',
    rainfall=25.5,
    temperature=32.0,
    humidity=75.0,
    date=date.today()
)
```

### Create Market Price
```python
price = MarketPrice.objects.create(
    crop='paddy',
    region='Vijayawada',
    price_per_quintal=2150.00,
    date=date.today(),
    is_peak_season=False
)
```

### Create Prediction Result
```python
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
    recommendation_reason='Peak season in 30 days. 16.3% profit increase possible.',
    confidence_score=85.5
)
```

---

## 🔍 READ Operations

### Get Single Record
```python
# By ID
farmer = Farmer.objects.get(id=1)

# By field value
farmer = Farmer.objects.get(village='Pedana', crop='paddy')

# Get or return None if not found
farmer = Farmer.objects.filter(id=1).first()
```

### Get Multiple Records
```python
# All records
all_farmers = Farmer.objects.all()

# Filter
machili_farmers = Farmer.objects.filter(mandal='machilipatnam')
paddy_farmers = Farmer.objects.filter(crop='paddy')
urgent_farmers = Farmer.objects.filter(urgent_cash=True)

# Multiple filters (AND)
result = Farmer.objects.filter(
    mandal='machilipatnam',
    crop='paddy',
    acres__gte=5.0  # Greater than or equal to 5
)

# OR conditions
from django.db.models import Q
result = Farmer.objects.filter(
    Q(mandal='machilipatnam') | Q(mandal='gudivada')
)

# Exclude
not_urgent = Farmer.objects.exclude(urgent_cash=True)
```

### Count Records
```python
# Total count
total = Farmer.objects.count()

# Filtered count
paddy_count = Farmer.objects.filter(crop='paddy').count()
```

### Ordering
```python
# Ascending
farmers = Farmer.objects.order_by('acres')

# Descending
farmers = Farmer.objects.order_by('-created_at')

# Multiple fields
farmers = Farmer.objects.order_by('mandal', '-acres')
```

### Limit Results
```python
# First 10
farmers = Farmer.objects.all()[:10]

# Records 10-20
farmers = Farmer.objects.all()[10:20]

# Get first
first = Farmer.objects.first()

# Get last
last = Farmer.objects.last()
```

### Related Data
```python
# Get farmer with diseases (forward relation)
farmer = Farmer.objects.get(id=1)
diseases = farmer.diseases.all()

# Get disease with farmer (reverse relation)
disease = DiseaseRecord.objects.get(id=1)
farmer = disease.farmer

# Get farmer with prediction (one-to-one)
farmer = Farmer.objects.get(id=1)
prediction = farmer.prediction
```

### Select Related (Optimize queries)
```python
# Load related farmer with disease (forward FK)
diseases = DiseaseRecord.objects.select_related('farmer').all()

# Load related prediction with farmer (OneToOne)
predictions = PredictionResult.objects.select_related('farmer').all()
```

### Prefetch Related (Optimize reverse relations)
```python
# Load farmers with all their diseases
farmers = Farmer.objects.prefetch_related('diseases').all()

# Now you can access diseases without extra queries
for farmer in farmers:
    for disease in farmer.diseases.all():
        print(disease.disease_name)
```

---

## ✏️ UPDATE Operations

### Update Single Record
```python
# Method 1: Get and save
farmer = Farmer.objects.get(id=1)
farmer.acres = 6.0
farmer.cold_storage = True
farmer.save()

# Method 2: Update directly
Farmer.objects.filter(id=1).update(acres=6.0, cold_storage=True)
```

### Update Multiple Records
```python
# Update all farmers in a mandal
Farmer.objects.filter(mandal='machilipatnam').update(cold_storage=True)

# Update all paddy farmers
Farmer.objects.filter(crop='paddy').update(urgent_cash=False)
```

---

## 🗑️ DELETE Operations

### Delete Single Record
```python
# Method 1: Get and delete
farmer = Farmer.objects.get(id=1)
farmer.delete()

# Method 2: Delete directly
Farmer.objects.filter(id=1).delete()
```

### Delete Multiple Records
```python
# Delete all farmers from a village
Farmer.objects.filter(village='Pedana').delete()

# Delete old weather data
old_date = date.today() - timedelta(days=365)
WeatherData.objects.filter(date__lt=old_date).delete()
```

### Cascade Delete
```python
# When farmer is deleted, related records are auto-deleted
farmer = Farmer.objects.get(id=1)
farmer.delete()  # Also deletes all DiseaseRecords and PredictionResult for this farmer
```

---

## 🔎 Advanced Queries

### Aggregation
```python
from django.db.models import Avg, Sum, Count, Min, Max

# Average acres
avg_acres = Farmer.objects.aggregate(Avg('acres'))

# Total acres by mandal
from django.db.models import Sum
mandal_totals = Farmer.objects.values('mandal').annotate(total_acres=Sum('acres'))

# Count by crop
crop_counts = Farmer.objects.values('crop').annotate(count=Count('id'))

# Average yield loss by severity
avg_loss = DiseaseRecord.objects.values('severity').annotate(avg_loss=Avg('yield_loss_percentage'))
```

### Date Queries
```python
from datetime import date, timedelta

# Today's weather
today_weather = WeatherData.objects.filter(date=date.today())

# Last 7 days
week_ago = date.today() - timedelta(days=7)
recent_weather = WeatherData.objects.filter(date__gte=week_ago)

# Between dates
start = date(2026, 1, 1)
end = date(2026, 1, 31)
january_data = WeatherData.objects.filter(date__range=[start, end])

# This month
from django.utils import timezone
this_month = WeatherData.objects.filter(date__month=timezone.now().month)
```

### Field Lookups
```python
# Greater than
large_farms = Farmer.objects.filter(acres__gt=10.0)

# Greater than or equal
large_farms = Farmer.objects.filter(acres__gte=5.0)

# Less than
small_farms = Farmer.objects.filter(acres__lt=2.0)

# Contains (case-insensitive)
farmers = Farmer.objects.filter(village__icontains='pada')

# Starts with
farmers = Farmer.objects.filter(village__startswith='Ped')

# In list
mandals = Farmer.objects.filter(mandal__in=['machilipatnam', 'gudivada'])

# Is null
no_prediction = Farmer.objects.filter(prediction__isnull=True)
```

---

## 📊 Useful Queries for Forecasting

### Get Farmers Ready for Harvest
```python
# Farmers who sowed 120+ days ago (paddy harvest time)
harvest_ready = Farmer.objects.filter(
    crop='paddy',
    sowing_date__lte=date.today() - timedelta(days=120)
)
```

### Get High Severity Diseases
```python
severe_diseases = DiseaseRecord.objects.filter(
    severity='high',
    yield_loss_percentage__gte=20.0
).select_related('farmer')
```

### Get Current Prices for Crops
```python
from django.db.models import Max

# Latest price for each crop
latest_prices = MarketPrice.objects.values('crop').annotate(
    latest_date=Max('date')
)
```

### Get Store Recommendations with High Profit
```python
good_stores = PredictionResult.objects.filter(
    recommendation='store',
    profit_delta__gte=10000,
    confidence_score__gte=70.0
).select_related('farmer')
```

### Get Weather Trends
```python
# Average temperature by mandal for last 30 days
from django.db.models import Avg
from datetime import timedelta

last_month = date.today() - timedelta(days=30)
avg_temps = WeatherData.objects.filter(
    date__gte=last_month
).values('mandal').annotate(
    avg_temp=Avg('temperature'),
    avg_rainfall=Avg('rainfall')
)
```

---

## 🎯 Testing Models in Shell

### Quick Test Sequence
```python
# 1. Create test farmer
farmer = Farmer.objects.create(
    mandal='machilipatnam',
    village='Test Village',
    crop='paddy',
    acres=3.0,
    sowing_date=date(2026, 1, 1),
    cold_storage=False,
    urgent_cash=False
)

# 2. Add disease
disease = DiseaseRecord.objects.create(
    farmer=farmer,
    disease_name='Test Disease',
    severity='medium',
    yield_loss_percentage=10.0
)

# 3. Add prediction
prediction = PredictionResult.objects.create(
    farmer=farmer,
    predicted_yield=50.0,
    yield_reduction_percentage=10.0,
    current_market_price=2000.0,
    total_current_value=100000.0,
    predicted_peak_price=2300.0,
    total_future_value=115000.0,
    profit_delta=15000.0,
    recommendation='store',
    recommendation_reason='Test recommendation',
    confidence_score=80.0
)

# 4. Test relationships
print(f"Farmer: {farmer}")
print(f"Diseases: {farmer.diseases.count()}")
print(f"Prediction: {farmer.prediction}")
print(f"Profit %: {farmer.prediction.profit_percentage()}%")

# 5. Clean up
farmer.delete()  # Cascades to disease and prediction
```

---

## 📋 Common Admin Tasks

### View All Data
```python
# Count records in each table
print(f"Farmers: {Farmer.objects.count()}")
print(f"Diseases: {DiseaseRecord.objects.count()}")
print(f"Weather: {WeatherData.objects.count()}")
print(f"Prices: {MarketPrice.objects.count()}")
print(f"Predictions: {PredictionResult.objects.count()}")
```

### Data Summary
```python
# Farmers by mandal
for mandal in ['machilipatnam', 'gudivada', 'vuyyur']:
    count = Farmer.objects.filter(mandal=mandal).count()
    print(f"{mandal}: {count} farmers")

# Crops grown
from django.db.models import Count
crops = Farmer.objects.values('crop').annotate(count=Count('id'))
for crop in crops:
    print(f"{crop['crop']}: {crop['count']} farmers")
```

---

## 💡 Tips & Best Practices

1. **Always use select_related() for forward FK**
   ```python
   # Good
   diseases = DiseaseRecord.objects.select_related('farmer').all()
   
   # Bad (N+1 queries)
   diseases = DiseaseRecord.objects.all()
   for d in diseases:
       print(d.farmer.village)  # Extra query each time!
   ```

2. **Use prefetch_related() for reverse relations**
   ```python
   # Good
   farmers = Farmer.objects.prefetch_related('diseases').all()
   
   # Bad
   farmers = Farmer.objects.all()
   for f in farmers:
       print(f.diseases.count())  # Extra query!
   ```

3. **Use update() for bulk updates**
   ```python
   # Good
   Farmer.objects.filter(mandal='machilipatnam').update(cold_storage=True)
   
   # Bad
   for farmer in Farmer.objects.filter(mandal='machilipatnam'):
       farmer.cold_storage = True
       farmer.save()  # One query per farmer!
   ```

4. **Use exists() instead of count() for checking**
   ```python
   # Good
   if Farmer.objects.filter(village='Pedana').exists():
       print("Farmers found")
   
   # Bad
   if Farmer.objects.filter(village='Pedana').count() > 0:
       print("Farmers found")
   ```

---

## 🚀 Ready to Use!

Access admin panel: http://127.0.0.1:8000/admin/

Create superuser first:
```bash
python manage.py createsuperuser
```

**All models are ready for data entry and testing!** ✅
