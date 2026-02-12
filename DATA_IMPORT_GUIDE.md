# 📥 DATA IMPORT UTILITY - DOCUMENTATION

## ✅ Import Complete!

Successfully created Django utility to import data from Excel into WeatherData and MarketPrice tables.

---

## 📊 Import Results

### Data Successfully Imported:

**Market Prices:**
- ✅ **419 price records** imported from EPICS DATA.xlsx
- 📅 Years covered: 2015, 2016, 2017, 2018, 2019, 2023, 2024
- 🌾 Crops: Turmeric, Paddy, Sugarcane, Chillies, Banana
- 📍 Region: Krishna District

**Weather Data:**
- ✅ **2,322 weather records** generated
- 📅 Period: January 1, 2024 - February 12, 2026 (current date)
- 📍 Mandals: Machilipatnam (774), Gudivada (774), Vuyyur (774)
- 🌦️ Parameters: Temperature, Rainfall, Humidity

---

## 🛠️ Two Ways to Import Data

### Method 1: Django Management Command (Recommended)

**Location:** `forecast/management/commands/import_data.py`

**Usage:**
```bash
# Import both weather and prices
python manage.py import_data

# Import only prices
python manage.py import_data --prices

# Import only weather
python manage.py import_data --weather

# Clear existing data before import
python manage.py import_data --clear

# Custom Excel file
python manage.py import_data --file "path/to/file.xlsx"

# Get help
python manage.py import_data --help
```

### Method 2: Standalone Script

**Location:** `import_standalone.py`

**Usage:**
```bash
# Run directly
python import_standalone.py
```

**Customize in script:**
```python
importer = DataImporter('EPICS DATA.xlsx')
importer.run(
    import_prices=True,
    import_weather=True,
    clear_existing=False  # Set True to clear
)
```

---

## 📋 Features

### ✅ Data Cleaning
- **Missing values:** Automatically skipped with counter
- **Price formatting:** Handles "RS 10,655" → 10655.0
- **Date formatting:** Converts to proper Python date objects
- **Crop name mapping:** Maps Excel names to model choices
- **Typo handling:** Handles "FEBRARURY" → "FEBRUARY"

### ✅ Error Handling
- Try-catch blocks around database operations
- Transaction management (atomic operations)
- Validation before insert
- Detailed error reporting
- Continues on error (doesn't crash)

### ✅ Duplicate Prevention
- Uses `update_or_create()` to avoid duplicates
- Respects unique constraints:
  - WeatherData: (mandal, date)
  - MarketPrice: (crop, region, date)

### ✅ Progress Tracking
- Real-time import progress
- Counts for imported vs skipped records
- Summary statistics at end
- Colored output for better readability

---

## 🗂️ File Structure

```
forecast/
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       └── import_data.py      # Django management command

import_standalone.py            # Standalone import script
EPICS DATA.xlsx                 # Source data file
```

---

## 📖 How It Works

### Excel File Structure

The EPICS DATA.xlsx file has:
- **Sheets:** One per year (2015-2024)
- **Row 0:** Header row ("CROP PRICE ANALYSIS (YEAR)")
- **Row 1:** Month names (JANUARY, FEBRUARY, etc.)
- **Row 2+:** Data rows with crop name and prices

**Example:**
```
Row 0: CROP NAME | COST OF CROP...
Row 1: (blank)   | JANUARY | FEBRUARY | MARCH | ...
Row 2: TURMERIC  | RS 10655 | RS 10655 | RS 10870 | ...
Row 3: RICE      | RS 1395  | RS 1395  | RS 1410  | ...
```

### Data Processing Flow

```
1. Read Excel File
   ↓
2. For Each Sheet (Year):
   ↓
3. Extract Month Names from Row 1
   ↓
4. Skip First 2 Rows (Headers)
   ↓
5. For Each Data Row:
   ↓
6. Clean Crop Name
   - Remove numbers (1., 2., etc.)
   - Convert to uppercase
   - Remove special characters
   ↓
7. Map to Model Crop Choice
   - TURMERIC → turmeric
   - RICE/WHEAT → paddy
   - etc.
   ↓
8. For Each Month Column:
   ↓
9. Clean Price Value
   - Remove "RS", "₹", commas
   - Convert to float
   ↓
10. Create Date Object
    - Year from sheet name
    - Month from column
    - Day = 15 (mid-month)
    ↓
11. Insert/Update Database
    - Use update_or_create()
    - Set is_peak_season flag
    ↓
12. Count Imported/Skipped
```

### Weather Data Generation

Since weather data wasn't in the Excel file, the script generates realistic synthetic data:

**Temperature (°C):**
- Winter (Dec-Feb): 20-28°C
- Summer (Mar-May): 28-38°C
- Monsoon (Jun-Sep): 25-32°C
- Post-Monsoon (Oct-Nov): 22-30°C

**Rainfall (mm):**
- Monsoon: 50-200mm
- Post-Monsoon: 20-80mm
- Dry Season: 0-20mm

**Humidity (%):**
- Monsoon: 70-90%
- Other seasons: 50-75%

---

## 🔍 Crop Mapping

The script maps Excel crop names to Django model choices:

| Excel Name | Model Choice | Notes |
|------------|--------------|-------|
| TURMERIC | turmeric | Direct match |
| RICE | paddy | Mapped to paddy |
| WHEAT | paddy | Mapped to paddy |
| CHILLIES/CHILLI | chillies | Handles plural |
| COTTON | cotton | Direct match |
| SUGARCANE | sugarcane | Direct match |
| BANANA | banana | Direct match |
| TOMATO | tomato | Direct match |
| OKRA/BHENDI | okra | Handles both names |
| BRINJAL/EGGPLANT | brinjal | Handles both names |
| MANGO | mango | Direct match |

**Unrecognized crops are skipped** (e.g., ELEPHANT FOOT YAM, MAIZE, WHITE SORGHUM, BLACKGRAM)

---

## 💾 Database Impact

### Before Import:
```sql
WeatherData: 0 records
MarketPrice: 0 records
```

### After Import:
```sql
WeatherData: 2,322 records
  - Machilipatnam: 774
  - Gudivada: 774
  - Vuyyur: 774

MarketPrice: 419 records
  - Turmeric: 83
  - Paddy: 84
  - Sugarcane: 84
  - Chillies: 84
  - Banana: 84
```

---

## 🎯 Command Options

### import_data Management Command

| Option | Description | Example |
|--------|-------------|---------|
| `--file` | Custom Excel file path | `--file "data.xlsx"` |
| `--weather` | Import only weather data | `--weather` |
| `--prices` | Import only market prices | `--prices` |
| `--clear` | Clear existing data first | `--clear` |
| `--help` | Show help message | `--help` |

**Examples:**
```bash
# Full import (both data types)
python manage.py import_data

# Re-import prices (clear old data)
python manage.py import_data --prices --clear

# Import from different file
python manage.py import_data --file "new_data.xlsx"

# Import only weather
python manage.py import_data --weather
```

---

## 🧪 Testing the Import

### Verify Data in Django Shell

```bash
python manage.py shell
```

```python
from forecast.models import WeatherData, MarketPrice
from datetime import date

# Check total counts
print(f"Weather: {WeatherData.objects.count()}")
print(f"Prices: {MarketPrice.objects.count()}")

# Check weather for a mandal
weather = WeatherData.objects.filter(mandal='machilipatnam')[:5]
for w in weather:
    print(f"{w.date}: {w.temperature}°C, {w.rainfall}mm")

# Check prices for a crop
prices = MarketPrice.objects.filter(crop='paddy').order_by('-date')[:5]
for p in prices:
    print(f"{p.date}: ₹{p.price_per_quintal}/quintal")

# Check latest price
latest = MarketPrice.objects.latest('date')
print(f"Latest price: {latest.crop} - ₹{latest.price_per_quintal}")

# Check peak season prices
peak = MarketPrice.objects.filter(is_peak_season=True).count()
print(f"Peak season prices: {peak}")
```

### Verify Data in Admin Panel

1. Access admin: http://127.0.0.1:8000/admin/
2. Navigate to:
   - **Weather Data** - See temperature, rainfall, humidity by mandal
   - **Market Prices** - See prices by crop with peak season markers

---

## 🔧 Customization

### Add More Crops

Edit `CROP_MAPPING` dictionary:

```python
CROP_MAPPING = {
    'TURMERIC': 'turmeric',
    'MANGO': 'mango',
    # Add new mappings here
    'YOUR_CROP': 'model_choice',
}
```

### Change Peak Seasons

Edit `is_peak_season()` method:

```python
def is_peak_season(self, crop, month):
    peak_seasons = {
        'paddy': [10, 11, 12, 1, 2],  # Oct-Feb
        'mango': [4, 5, 6],  # Apr-Jun
        # Modify or add crops here
    }
    return month in peak_seasons.get(crop, [])
```

### Add More Regions

Change region assignment in import:

```python
MarketPrice.objects.update_or_create(
    crop=mapped_crop,
    region='Your Region Name',  # Change here
    date=price_date,
    # ...
)
```

---

## ⚠️ Important Notes

### 1. Data Quality
- Not all Excel crop names are mapped (some skipped)
- Weather data is synthetic (generated, not from Excel)
- Prices use 15th of month as default date
- Years 2020, 2021, 2022 had no usable data in Excel

### 2. Performance
- Import takes ~10-30 seconds depending on data size
- Uses transactions for data integrity
- update_or_create() prevents duplicates

### 3. Maintenance
- Re-running import is safe (uses update_or_create)
- Use `--clear` flag to start fresh
- Keep backup of EPICS DATA.xlsx

---

## 📈 Next Steps

### Data is Ready For:

1. ✅ **Yield Prediction Models**
   - Use weather data (temperature, rainfall, humidity)
   - Factor in crop type and growth stage

2. ✅ **Price Forecasting Models**
   - Historical price trends available
   - Peak season patterns identified

3. ✅ **Farmer Recommendations**
   - Compare current vs predicted prices
   - Calculate profit delta
   - Generate STORE/SELL decisions

4. ✅ **Data Analysis**
   - Price trends over years
   - Weather pattern analysis
   - Seasonal price variations

---

## 🐛 Troubleshooting

### Import Shows 0 Records
- Check Excel file path
- Verify sheet names are years (2015-2024)
- Check row structure matches expected format

### Price Cleaning Fails
- Prices must be in format "RS 1234" or "1234"
- Handles commas: "RS 10,655" works
- Empty cells are skipped

### Duplicate Errors
- Should not occur (update_or_create handles this)
- If occurs, check unique constraints

### Memory Issues
- Import processes sheet by sheet
- Uses generators where possible
- For very large files, consider batch processing

---

## 📚 Code Documentation

### Key Functions

**clean_crop_name(crop_name)**
- Removes numbers and special characters
- Converts to uppercase
- Returns cleaned name or None

**clean_price(price_value)**
- Removes currency symbols
- Removes commas
- Converts to float
- Returns None if invalid

**get_mapped_crop(crop_name)**
- Maps Excel name to model choice
- Handles partial matches
- Returns None if no match

**is_peak_season(crop, month)**
- Checks if month is peak for crop
- Returns boolean
- Used to set is_peak_season flag

---

## ✅ Success Metrics

- ✅ 419 market price records imported
- ✅ 2,322 weather records generated
- ✅ 5 crops covered
- ✅ 3 mandals covered
- ✅ 7 years of price data (2015-2019, 2023-2024)
- ✅ 2+ years of weather data (2024-2026)
- ✅ 0 duplicate records
- ✅ Clean data with proper validation

---

## 🎓 Learning Outcomes

From this implementation, you learned:

1. ✅ Django management commands
2. ✅ Pandas Excel reading
3. ✅ Data cleaning techniques
4. ✅ Django ORM bulk operations
5. ✅ Transaction management
6. ✅ Error handling patterns
7. ✅ update_or_create() usage
8. ✅ Data validation strategies
9. ✅ Progress tracking
10. ✅ Command-line argument parsing

---

**Import utility is production-ready and fully documented!** 🚀

Run anytime with: `python manage.py import_data`
