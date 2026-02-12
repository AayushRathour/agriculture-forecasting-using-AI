"""
Standalone Data Import Script
Alternative to Django management command
Can be run directly: python import_standalone.py
"""

import os
import sys
import django
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agri_forecast.settings')
django.setup()

from django.db import transaction
from forecast.models import WeatherData, MarketPrice


class DataImporter:
    """Handles data import from Excel to database"""
    
    # Crop name mapping
    CROP_MAPPING = {
        'TURMERIC': 'turmeric',
        'WHEAT': 'paddy',
        'PADDY': 'paddy',
        'RICE': 'paddy',
        'MANGO': 'mango',
        'CHILLIES': 'chillies',
        'CHILLI': 'chillies',
        'COTTON': 'cotton',
        'SUGARCANE': 'sugarcane',
        'BANANA': 'banana',
        'TOMATO': 'tomato',
        'OKRA': 'okra',
        'BHENDI': 'okra',
        'BRINJAL': 'brinjal',
        'EGGPLANT': 'brinjal',
    }
    
    MONTH_MAPPING = {
        'JANUARY': 1, 'FEBRUARY': 2, 'MARCH': 3, 'APRIL': 4,
        'MAY': 5, 'JUNE': 6, 'JULY': 7, 'AUGUST': 8,
        'SEPTEMBER': 9, 'OCTOBER': 10, 'NOVEMBER': 11, 'DECEMBER': 12
    }
    
    def __init__(self, file_path='EPICS DATA.xlsx'):
        self.file_path = file_path
        self.stats = {
            'prices_imported': 0,
            'prices_skipped': 0,
            'weather_imported': 0,
            'weather_skipped': 0
        }
    
    def run(self, import_prices=True, import_weather=True, clear_existing=False):
        """Main execution method"""
        print('=' * 70)
        print('📊 DATA IMPORT STARTED')
        print('=' * 70)
        
        try:
            if clear_existing:
                self.clear_data(import_weather, import_prices)
            
            if import_prices:
                self.import_market_prices()
            
            if import_weather:
                self.import_weather_data()
            
            self.print_summary()
            
            print('\n' + '=' * 70)
            print('✅ DATA IMPORT COMPLETED SUCCESSFULLY!')
            print('=' * 70)
            
        except Exception as e:
            print(f'\n❌ ERROR: {str(e)}')
            raise
    
    def clear_data(self, clear_weather, clear_prices):
        """Clear existing data"""
        print('\n🗑️  Clearing existing data...')
        
        if clear_weather:
            count = WeatherData.objects.all().delete()[0]
            print(f'   Deleted {count} weather records')
        
        if clear_prices:
            count = MarketPrice.objects.all().delete()[0]
            print(f'   Deleted {count} price records')
    
    def import_market_prices(self):
        """Import market prices from Excel"""
        print(f'\n💰 Importing Market Prices from: {self.file_path}')
        
        try:
            excel_file = pd.ExcelFile(self.file_path)
            print(f'✅ Found {len(excel_file.sheet_names)} sheets')
            
            for sheet_name in excel_file.sheet_names:
                try:
                    year = int(sheet_name)
                    print(f'\n   Processing year: {year}')
                    
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    imported, skipped = self._parse_price_sheet(df, year)
                    
                    self.stats['prices_imported'] += imported
                    self.stats['prices_skipped'] += skipped
                    
                    print(f'   ✅ Imported: {imported}, Skipped: {skipped}')
                    
                except ValueError:
                    print(f'   ⚠️  Skipping non-year sheet: {sheet_name}')
                    continue
        
        except FileNotFoundError:
            print(f'❌ File not found: {self.file_path}')
            raise
    
    def _parse_price_sheet(self, df, year):
        """Parse a single price sheet"""
        imported = 0
        skipped = 0
        
        # Clean dataframe
        df = df.replace([np.nan, 'nan', 'NaN', 'NAN'], None)
        
        # Identify crop column
        crop_col = df.columns[0]
        
        # Find month columns
        month_cols = []
        for col in df.columns[1:]:
            col_upper = str(col).upper().strip()
            if col_upper in self.MONTH_MAPPING:
                month_cols.append((col, self.MONTH_MAPPING[col_upper]))
        
        # Process rows
        for idx, row in df.iterrows():
            crop_name = self._clean_crop_name(str(row[crop_col]))
            if not crop_name:
                continue
            
            mapped_crop = self._get_mapped_crop(crop_name)
            if not mapped_crop:
                continue
            
            for col, month_num in month_cols:
                price = self._clean_price(row[col])
                if price is None or price <= 0:
                    skipped += 1
                    continue
                
                try:
                    price_date = date(year, month_num, 15)
                    
                    with transaction.atomic():
                        obj, created = MarketPrice.objects.update_or_create(
                            crop=mapped_crop,
                            region='Krishna District',
                            date=price_date,
                            defaults={
                                'price_per_quintal': price,
                                'is_peak_season': self._is_peak_season(mapped_crop, month_num)
                            }
                        )
                        if created:
                            imported += 1
                
                except Exception as e:
                    skipped += 1
        
        return imported, skipped
    
    def _clean_crop_name(self, crop_name):
        """Clean crop name"""
        if not crop_name or crop_name == 'nan':
            return None
        
        crop_name = str(crop_name).upper().strip()
        crop_name = ''.join(c for c in crop_name if c.isalpha() or c.isspace())
        
        # Remove numbering
        for i in range(1, 11):
            prefix = f'{i}.'
            if crop_name.startswith(prefix):
                crop_name = crop_name[len(prefix):].strip()
        
        return crop_name if crop_name else None
    
    def _get_mapped_crop(self, crop_name):
        """Map crop name to model choice"""
        crop_upper = crop_name.upper()
        
        if crop_upper in self.CROP_MAPPING:
            return self.CROP_MAPPING[crop_upper]
        
        for key, value in self.CROP_MAPPING.items():
            if key in crop_upper:
                return value
        
        return None
    
    def _clean_price(self, price_value):
        """Clean and parse price"""
        if pd.isna(price_value) or price_value is None:
            return None
        
        price_str = str(price_value).upper().replace('RS', '').replace('₹', '').replace(',', '').strip()
        
        try:
            return float(price_str)
        except:
            return None
    
    def _is_peak_season(self, crop, month):
        """Check if peak season"""
        peak_seasons = {
            'paddy': [10, 11, 12, 1, 2],
            'mango': [4, 5, 6],
            'chillies': [1, 2, 3],
            'turmeric': [1, 2, 3],
            'cotton': [11, 12, 1],
            'sugarcane': [12, 1, 2, 3],
            'banana': list(range(1, 13)),
            'tomato': [11, 12, 1, 2],
            'okra': [10, 11, 12, 1],
            'brinjal': [10, 11, 12, 1, 2],
        }
        return month in peak_seasons.get(crop, [])
    
    def import_weather_data(self):
        """Generate weather data"""
        print('\n🌦️  Generating Weather Data...')
        
        mandals = ['machilipatnam', 'gudivada', 'vuyyur']
        start_date = date(2024, 1, 1)
        end_date = date.today()
        
        for mandal in mandals:
            current_date = start_date
            
            while current_date <= end_date:
                month = current_date.month
                
                # Seasonal temperature
                if month in [12, 1, 2]:
                    temp = np.random.uniform(20, 28)
                elif month in [3, 4, 5]:
                    temp = np.random.uniform(28, 38)
                elif month in [6, 7, 8, 9]:
                    temp = np.random.uniform(25, 32)
                else:
                    temp = np.random.uniform(22, 30)
                
                # Seasonal rainfall
                if month in [6, 7, 8, 9]:
                    rainfall = np.random.uniform(50, 200)
                elif month in [10, 11]:
                    rainfall = np.random.uniform(20, 80)
                else:
                    rainfall = np.random.uniform(0, 20)
                
                # Seasonal humidity
                humidity = np.random.uniform(70, 90) if month in [6, 7, 8, 9] else np.random.uniform(50, 75)
                
                try:
                    with transaction.atomic():
                        obj, created = WeatherData.objects.update_or_create(
                            mandal=mandal,
                            date=current_date,
                            defaults={
                                'temperature': round(temp, 1),
                                'rainfall': round(rainfall, 1),
                                'humidity': round(humidity, 1)
                            }
                        )
                        if created:
                            self.stats['weather_imported'] += 1
                except:
                    self.stats['weather_skipped'] += 1
                
                current_date += timedelta(days=1)
        
        print(f'✅ Weather records generated: {self.stats["weather_imported"]}')
    
    def print_summary(self):
        """Print import summary"""
        print('\n' + '=' * 70)
        print('📊 IMPORT SUMMARY')
        print('=' * 70)
        print(f'\n💰 Market Prices:')
        print(f'   Imported: {self.stats["prices_imported"]}')
        print(f'   Skipped: {self.stats["prices_skipped"]}')
        
        print(f'\n🌦️  Weather Data:')
        print(f'   Imported: {self.stats["weather_imported"]}')
        print(f'   Skipped: {self.stats["weather_skipped"]}')
        
        print(f'\n📈 Database Totals:')
        print(f'   Market Prices: {MarketPrice.objects.count()}')
        print(f'   Weather Records: {WeatherData.objects.count()}')


if __name__ == '__main__':
    """Run import when script is executed directly"""
    print('\n🚀 Starting Data Import...\n')
    
    importer = DataImporter('EPICS DATA.xlsx')
    importer.run(
        import_prices=True,
        import_weather=True,
        clear_existing=False  # Set to True to clear existing data
    )
