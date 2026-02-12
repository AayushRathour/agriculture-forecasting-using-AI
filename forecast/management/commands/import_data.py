"""
Django Management Command: Import Data from Excel
Reads EPICS DATA.xlsx and populates WeatherData and MarketPrice tables
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from forecast.models import WeatherData, MarketPrice


class Command(BaseCommand):
    """
    Import weather and market price data from Excel file
    Usage: python manage.py import_data
    """
    
    help = 'Import weather and market price data from EPICS DATA.xlsx'
    
    # Crop name mapping (Excel names to model choices)
    CROP_MAPPING = {
        'TURMERIC': 'turmeric',
        'WHEAT': 'paddy',  # Using paddy as substitute
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
    
    # Month name to number mapping
    MONTH_MAPPING = {
        'JANUARY': 1, 'FEBRUARY': 2, 'MARCH': 3, 'APRIL': 4,
        'MAY': 5, 'JUNE': 6, 'JULY': 7, 'AUGUST': 8,
        'SEPTEMBER': 9, 'OCTOBER': 10, 'NOVEMBER': 11, 'DECEMBER': 12
    }
    
    def add_arguments(self, parser):
        """Add command line arguments"""
        parser.add_argument(
            '--file',
            type=str,
            default='EPICS DATA.xlsx',
            help='Path to Excel file (default: EPICS DATA.xlsx)'
        )
        parser.add_argument(
            '--weather',
            action='store_true',
            help='Import only weather data'
        )
        parser.add_argument(
            '--prices',
            action='store_true',
            help='Import only market prices'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before import'
        )
    
    def handle(self, *args, **options):
        """Main command handler"""
        file_path = options['file']
        import_weather = options['weather'] or not options['prices']
        import_prices = options['prices'] or not options['weather']
        clear_data = options['clear']
        
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('📊 DATA IMPORT STARTED'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        try:
            # Clear existing data if requested
            if clear_data:
                self.clear_existing_data(import_weather, import_prices)
            
            # Read Excel file
            self.stdout.write(f'\n📂 Reading file: {file_path}')
            excel_file = pd.ExcelFile(file_path)
            self.stdout.write(f'✅ Found {len(excel_file.sheet_names)} sheets')
            
            # Import data
            if import_prices:
                self.import_market_prices(excel_file)
            
            if import_weather:
                self.import_weather_data()
            
            # Summary
            self.print_summary()
            
            self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
            self.stdout.write(self.style.SUCCESS('✅ DATA IMPORT COMPLETED SUCCESSFULLY!'))
            self.stdout.write(self.style.SUCCESS('=' * 70))
            
        except FileNotFoundError:
            raise CommandError(f'File not found: {file_path}')
        except Exception as e:
            raise CommandError(f'Import failed: {str(e)}')
    
    def clear_existing_data(self, clear_weather, clear_prices):
        """Clear existing data from tables"""
        self.stdout.write('\n🗑️  Clearing existing data...')
        
        if clear_weather:
            count = WeatherData.objects.all().delete()[0]
            self.stdout.write(f'   Deleted {count} weather records')
        
        if clear_prices:
            count = MarketPrice.objects.all().delete()[0]
            self.stdout.write(f'   Deleted {count} price records')
    
    def import_market_prices(self, excel_file):
        """Import market price data from Excel sheets"""
        self.stdout.write('\n💰 Importing Market Prices...')
        
        total_imported = 0
        total_skipped = 0
        
        for sheet_name in excel_file.sheet_names:
            try:
                year = int(sheet_name)
                self.stdout.write(f'\n   Processing year: {year}')
                
                # Read sheet
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                # Parse and import data
                imported, skipped = self.parse_price_sheet(df, year)
                total_imported += imported
                total_skipped += skipped
                
                self.stdout.write(f'   ✅ Imported: {imported}, Skipped: {skipped}')
                
            except ValueError:
                self.stdout.write(f'   ⚠️  Skipping non-year sheet: {sheet_name}')
                continue
        
        self.stdout.write(f'\n✅ Total Market Prices Imported: {total_imported}')
        if total_skipped > 0:
            self.stdout.write(f'⚠️  Total Skipped: {total_skipped}')
    
    def parse_price_sheet(self, df, year):
        """Parse price data from a single sheet"""
        imported = 0
        skipped = 0
        
        # The Excel has: Row 0 = Header, Row 1 = Month names, Row 2+ = Data
        # Skip first two rows and use row 1 as column headers
        if len(df) < 2:
            return 0, 0
        
        # Extract month names from row 1 (index 1)
        month_row = df.iloc[1]
        month_cols = []
        
        for idx in range(1, len(df.columns)):
            month_name = str(month_row.iloc[idx]).upper().strip()
            # Handle typos like "FEBRARURY"
            if 'FEBR' in month_name:
                month_name = 'FEBRUARY'
            
            if month_name in self.MONTH_MAPPING:
                month_cols.append((idx, self.MONTH_MAPPING[month_name]))
        
        # Process data rows (skip first 2 rows - headers)
        df = df.iloc[2:]
        
        # First column has crop names
        crop_col = 0
        
        # Process each row
        for idx, row in df.iterrows():
            crop_name = self.clean_crop_name(str(row.iloc[crop_col]))
            
            if not crop_name:
                continue
            
            # Get mapped crop
            mapped_crop = self.get_mapped_crop(crop_name)
            if not mapped_crop:
                continue
            
            # Process each month
            for col_idx, month_num in month_cols:
                price_value = row.iloc[col_idx]
                
                if pd.isna(price_value):
                    skipped += 1
                    continue
                
                # Clean and parse price
                price = self.clean_price(price_value)
                if price is None or price <= 0:
                    skipped += 1
                    continue
                
                # Create date (use 15th of month as default)
                try:
                    price_date = date(year, month_num, 15)
                except ValueError:
                    skipped += 1
                    continue
                
                # Create or update market price
                try:
                    with transaction.atomic():
                        obj, created = MarketPrice.objects.update_or_create(
                            crop=mapped_crop,
                            region='Krishna District',
                            date=price_date,
                            defaults={
                                'price_per_quintal': price,
                                'is_peak_season': self.is_peak_season(mapped_crop, month_num)
                            }
                        )
                        if created:
                            imported += 1
                except Exception as e:
                    self.stdout.write(f'      Error: {str(e)}')
                    skipped += 1
        
        return imported, skipped
    
    def clean_crop_name(self, crop_name):
        """Clean and standardize crop name"""
        if pd.isna(crop_name) or crop_name == 'nan':
            return None
        
        # Remove numbers and extra characters
        crop_name = str(crop_name).upper().strip()
        crop_name = ''.join(char for char in crop_name if char.isalpha() or char.isspace())
        crop_name = crop_name.strip()
        
        # Remove common prefixes
        for prefix in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.']:
            if crop_name.startswith(prefix):
                crop_name = crop_name[len(prefix):].strip()
        
        return crop_name if crop_name else None
    
    def get_mapped_crop(self, crop_name):
        """Map Excel crop name to model crop choice"""
        crop_upper = crop_name.upper()
        
        # Direct match
        if crop_upper in self.CROP_MAPPING:
            return self.CROP_MAPPING[crop_upper]
        
        # Partial match
        for key, value in self.CROP_MAPPING.items():
            if key in crop_upper or crop_upper in key:
                return value
        
        return None
    
    def clean_price(self, price_value):
        """Clean and parse price value"""
        if pd.isna(price_value):
            return None
        
        # Convert to string and clean
        price_str = str(price_value).upper().strip()
        
        # Remove currency symbols and text
        price_str = price_str.replace('RS', '').replace('₹', '').replace(',', '').strip()
        
        # Try to convert to float
        try:
            price = float(price_str)
            return price if price > 0 else None
        except (ValueError, TypeError):
            return None
    
    def is_peak_season(self, crop, month):
        """Determine if month is peak season for crop"""
        peak_seasons = {
            'paddy': [10, 11, 12, 1, 2],  # Oct-Feb
            'mango': [4, 5, 6],  # Apr-Jun
            'chillies': [1, 2, 3],  # Jan-Mar
            'turmeric': [1, 2, 3],  # Jan-Mar
            'cotton': [11, 12, 1],  # Nov-Jan
            'sugarcane': [12, 1, 2, 3],  # Dec-Mar
            'banana': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],  # Year-round
            'tomato': [11, 12, 1, 2],  # Nov-Feb
            'okra': [10, 11, 12, 1],  # Oct-Jan
            'brinjal': [10, 11, 12, 1, 2],  # Oct-Feb
        }
        
        return month in peak_seasons.get(crop, [])
    
    def import_weather_data(self):
        """Generate sample weather data for Krishna District mandals"""
        self.stdout.write('\n🌦️  Generating Weather Data...')
        
        mandals = ['machilipatnam', 'gudivada', 'vuyyur']
        start_date = date(2024, 1, 1)
        end_date = date(2026, 2, 12)  # Current date
        
        imported = 0
        
        # Generate weather data for each mandal
        for mandal in mandals:
            current_date = start_date
            
            while current_date <= end_date:
                # Generate realistic weather data based on season
                month = current_date.month
                
                # Temperature (°C) - varies by season
                if month in [12, 1, 2]:  # Winter
                    temp = np.random.uniform(20, 28)
                elif month in [3, 4, 5]:  # Summer
                    temp = np.random.uniform(28, 38)
                elif month in [6, 7, 8, 9]:  # Monsoon
                    temp = np.random.uniform(25, 32)
                else:  # Post-monsoon
                    temp = np.random.uniform(22, 30)
                
                # Rainfall (mm) - higher during monsoon
                if month in [6, 7, 8, 9]:  # Monsoon
                    rainfall = np.random.uniform(50, 200)
                elif month in [10, 11]:  # Post-monsoon
                    rainfall = np.random.uniform(20, 80)
                else:  # Dry season
                    rainfall = np.random.uniform(0, 20)
                
                # Humidity (%) - higher during monsoon
                if month in [6, 7, 8, 9]:  # Monsoon
                    humidity = np.random.uniform(70, 90)
                else:
                    humidity = np.random.uniform(50, 75)
                
                # Create weather record
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
                            imported += 1
                except Exception as e:
                    self.stdout.write(f'   Error: {str(e)}')
                
                # Move to next day
                from datetime import timedelta
                current_date += timedelta(days=1)
        
        self.stdout.write(f'✅ Total Weather Records Generated: {imported}')
    
    def print_summary(self):
        """Print import summary"""
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('📊 DATABASE SUMMARY')
        self.stdout.write('=' * 70)
        
        # Count records
        weather_count = WeatherData.objects.count()
        price_count = MarketPrice.objects.count()
        
        self.stdout.write(f'\n🌦️  Weather Data Records: {weather_count}')
        self.stdout.write(f'💰 Market Price Records: {price_count}')
        
        # Weather by mandal
        if weather_count > 0:
            self.stdout.write('\n   Weather Records by Mandal:')
            for mandal in ['machilipatnam', 'gudivada', 'vuyyur']:
                count = WeatherData.objects.filter(mandal=mandal).count()
                self.stdout.write(f'      {mandal.title()}: {count}')
        
        # Prices by crop
        if price_count > 0:
            self.stdout.write('\n   Market Prices by Crop:')
            crops = MarketPrice.objects.values_list('crop', flat=True).distinct()
            for crop in crops:
                count = MarketPrice.objects.filter(crop=crop).count()
                self.stdout.write(f'      {crop.title()}: {count}')
