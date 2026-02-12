"""
Quick verification script to check imported data
Run: python verify_data.py
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agri_forecast.settings')
django.setup()

from forecast.models import WeatherData, MarketPrice
from django.db import models

print('=' * 70)
print('📊 DATABASE VERIFICATION')
print('=' * 70)

# Count records
weather_count = WeatherData.objects.count()
price_count = MarketPrice.objects.count()

print(f'\n✅ Total Records:')
print(f'   Weather Data: {weather_count}')
print(f'   Market Prices: {price_count}')

# Weather by mandal
print(f'\n🌦️  Weather Records by Mandal:')
for mandal in ['machilipatnam', 'gudivada', 'vuyyur']:
    count = WeatherData.objects.filter(mandal=mandal).count()
    print(f'   {mandal.title()}: {count}')

# Sample weather data
print(f'\n📍 Sample Weather Data (Machilipatnam):')
for w in WeatherData.objects.filter(mandal='machilipatnam').order_by('date')[:5]:
    print(f'   {w.date}: {w.temperature}°C, {w.rainfall}mm, {w.humidity}%')

# Prices by crop
print(f'\n💰 Market Prices by Crop:')
crops = MarketPrice.objects.values_list('crop', flat=True).distinct()
for crop in crops:
    count = MarketPrice.objects.filter(crop=crop).count()
    print(f'   {crop.title()}: {count} records')

# Sample market prices
print(f'\n📈 Sample Market Prices (Paddy - Latest):')
for p in MarketPrice.objects.filter(crop='paddy').order_by('-date')[:5]:
    peak_indicator = '⭐' if p.is_peak_season else '  '
    print(f'   {peak_indicator} {p.date}: ₹{p.price_per_quintal:,.2f}/Q')

# Date ranges
weather_dates = WeatherData.objects.aggregate(
    min_date=models.Min('date'),
    max_date=models.Max('date')
)
price_dates = MarketPrice.objects.aggregate(
    min_date=models.Min('date'),
    max_date=models.Max('date')
)

print(f'\n📅 Date Ranges:')
print(f'   Weather: {weather_dates["min_date"]} to {weather_dates["max_date"]}')
print(f'   Prices: {price_dates["min_date"]} to {price_dates["max_date"]}')

print('\n' + '=' * 70)
print('✅ VERIFICATION COMPLETE!')
print('=' * 70)
