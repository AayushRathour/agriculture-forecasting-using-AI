"""
Management command to populate sample data for testing
Usage: python manage.py populate_sample_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from forecast.models import Farmer, DiseaseRecord, WeatherData, MarketPrice
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Populate database with sample data for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--farmers',
            type=int,
            default=10,
            help='Number of sample farmers to create'
        )
    
    def handle(self, *args, **options):
        num_farmers = options['farmers']
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🌱 Creating {num_farmers} sample farmer records...\n')
        )
        
        # Sample data
        villages = {
            'machilipatnam': ['Chilakalapudi', 'Avanigadda', 'Koduru', 'Nagayalanka'],
            'gudivada': ['Gudivada Urban', 'Gudivada Rural', 'Mudinepalli', 'Pedapalem'],
            'vuyyur': ['Vuyyuru Urban', 'Vuyyuru Rural', 'Jaggaiahpeta', 'Nandivada']
        }
        
        crops = ['paddy', 'mango', 'chillies', 'cotton', 'turmeric', 'banana']
        severities = ['low', 'medium', 'high']
        
        created_count = 0
        
        for i in range(num_farmers):
            # Random farmer data
            mandal = random.choice(list(villages.keys()))
            village = random.choice(villages[mandal])
            crop = random.choice(crops)
            acres = round(random.uniform(1.0, 10.0), 1)
            sowing_date = date.today() - timedelta(days=random.randint(30, 120))
            cold_storage = random.choice([True, False])
            urgent_cash = random.choice([True, False])
            
            farmer = Farmer.objects.create(
                mandal=mandal,
                village=village,
                crop=crop,
                acres=acres,
                sowing_date=sowing_date,
                cold_storage=cold_storage,
                urgent_cash=urgent_cash
            )
            
            created_count += 1
            self.stdout.write(f'   ✓ Created farmer {i+1}: {village} - {crop} ({acres} acres)')
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Successfully created {created_count} sample farmers!\n')
        )
