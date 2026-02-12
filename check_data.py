import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agri_forecast.settings')
django.setup()

from forecast.models import MarketPrice

print(f"Total Market Prices in DB: {MarketPrice.objects.count()}")
print("\nFirst 10 records:")
for price in MarketPrice.objects.all()[:10]:
    print(f"Crop: {price.crop}, Region: {price.region}, Price: ₹{price.price_per_quintal}, Date: {price.date}")

print("\nCrops in database:")
crops = MarketPrice.objects.values_list('crop', flat=True).distinct()
for crop in crops:
    count = MarketPrice.objects.filter(crop=crop).count()
    print(f"  {crop}: {count} records")
