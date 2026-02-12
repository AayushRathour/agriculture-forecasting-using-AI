import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agri_forecast.settings')
django.setup()

from forecast.models import MarketPrice

# Clear existing market price data
print("Clearing existing market price data...")
MarketPrice.objects.all().delete()

# 2023 Market Price Data - Month by Month
market_data_2023 = {
    'turmeric': [10655, 10655, 10870, 10870, 10870, 10870, 10772, 10772, 10772, 10655, 10655, 10655],
    'paddy': [1407, 1407, 1442, 1442, 1442, 1442, 1460, 1460, 1460, 1407, 1407, 1407],  # Rice
    'mango': [None] * 12,  # Perishable - no data
    'chillies': [11200, 11200, 11155, 11155, 11155, 11155, 11230, 11230, 11230, 11200, 11200, 11200],
    'cotton': [None] * 12,  # Not in Excel data
    'sugarcane': [2698, 2698, 2745, 2745, 2745, 2745, 2770, 2770, 2770, 2698, 2698, 2698],
    'banana': [1830, 1830, 1819, 1819, 1819, 1819, 1856, 1856, 1856, 1830, 1830, 1830],
    'tomato': [None] * 12,  # Perishable - no data
    'okra': [None] * 12,  # Perishable - no data (Ladies Finger)
    'brinjal': [None] * 12,  # No data in Excel
}

# Additional crops from Excel that aren't in current CROP_CHOICES
# These will be mapped to closest available crop or added as notes
additional_crops = {
    'wheat': [1501, 1501, 1484, 1484, 1484, 1484, 1469, 1470, 1469, 1501, 1501, 1501],
    'maize': [1100, 1100, 1080, 1080, 1080, 1080, 1055, 1055, 1055, 1100, 1100, 1100],
    'white_sorghum': [1858, 1858, 1902, 1902, 1902, 1902, 1880, 1880, 1880, 1858, 1858, 1858],
    'blackgram': [3623, 3623, 3701, 3701, 3701, 3701, 3674, 3674, 3674, 3623, 3623, 3623],
    'chickpeas': [5750, 5750, 5699, 5699, 5699, 5699, 5716, 5716, 5716, 5750, 5750, 5750],
    'sweet_potato': [1391, 1391, 1404, 1404, 1404, 1404, 1378, 1378, 1378, 1391, 1391, 1391],
}

months = ['January', 'February', 'March', 'April', 'May', 'June', 
          'July', 'August', 'September', 'October', 'November', 'December']

print("\nAdding 2023 market price data...")
count = 0

# Add data for crops that exist in model
for crop_key, prices in market_data_2023.items():
    for month_idx, price in enumerate(prices):
        if price is not None:  # Skip perishable crops with no data
            month = month_idx + 1
            market_date = date(2023, month, 15)  # Mid-month date
            
            MarketPrice.objects.create(
                crop=crop_key,
                region='Krishna District',
                price_per_quintal=price,
                date=market_date,
                is_peak_season=(month in [10, 11, 12, 1, 2])  # Peak season for most crops
            )
            count += 1
            print(f"Added: {crop_key} - {months[month_idx]} 2023 - ₹{price}")

print(f"\nTotal records added: {count}")
print(f"Total records in database: {MarketPrice.objects.count()}")

# Show summary by crop
print("\n=== Market Price Summary ===")
for crop_key in market_data_2023.keys():
    crop_count = MarketPrice.objects.filter(crop=crop_key).count()
    if crop_count > 0:
        avg_price = MarketPrice.objects.filter(crop=crop_key).aggregate(
            models.Avg('price_per_quintal')
        )['price_per_quintal__avg']
        print(f"{crop_key}: {crop_count} records, Avg Price: ₹{avg_price:.2f}")

print("\n✅ Market price data successfully loaded!")
print("\nNote: Additional crops from Excel (wheat, maize, sorghum, blackgram, chickpeas, sweet_potato)")
print("are not in the current CROP_CHOICES model. You may need to add them to the model if needed.")
