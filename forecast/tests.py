"""
Tests for the forecast app
Run tests with: python manage.py test
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from forecast.models import Farmer, WeatherData, MarketPrice
from datetime import date


class FarmerModelTest(TestCase):
    """Test the Farmer model"""
    
    def setUp(self):
        self.farmer = Farmer.objects.create(
            mandal='machilipatnam',
            village='Test Village',
            crop='paddy',
            acres=5.0,
            sowing_date=date.today(),
            cold_storage=True,
            urgent_cash=False
        )
    
    def test_farmer_creation(self):
        """Test that a farmer can be created"""
        self.assertIsInstance(self.farmer, Farmer)
        self.assertEqual(self.farmer.crop, 'paddy')
        self.assertEqual(self.farmer.acres, 5.0)
    
    def test_farmer_str(self):
        """Test the string representation"""
        expected = f"{self.farmer.village} - Paddy (Rice) ({self.farmer.acres} acres)"
        self.assertEqual(str(self.farmer), expected)
    
    def test_crop_age_days(self):
        """Test crop age calculation"""
        age = self.farmer.crop_age_days()
        self.assertEqual(age, 0)  # Created today


class ViewsTest(TestCase):
    """Test the views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_home_page(self):
        """Test home page loads"""
        response = self.client.get(reverse('forecast:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forecast/home.html')
    
    def test_farmer_input_requires_login(self):
        """Test that farmer input requires login"""
        response = self.client.get(reverse('forecast:farmer_input'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_farmer_input_authenticated(self):
        """Test farmer input page for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('forecast:farmer_input'))
        self.assertEqual(response.status_code, 200)
    
    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post(reverse('forecast:user_register'), {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'newpass123',
            'confirm_password': 'newpass123'
        })
        self.assertEqual(User.objects.filter(username='newuser').count(), 1)


class WeatherDataTest(TestCase):
    """Test WeatherData model"""
    
    def test_weather_creation(self):
        """Test weather data creation"""
        weather = WeatherData.objects.create(
            mandal='machilipatnam',
            rainfall=50.0,
            temperature=28.5,
            humidity=75.0,
            date=date.today()
        )
        self.assertIsInstance(weather, WeatherData)
        self.assertEqual(weather.temperature, 28.5)


class MarketPriceTest(TestCase):
    """Test MarketPrice model"""
    
    def test_price_creation(self):
        """Test market price creation"""
        price = MarketPrice.objects.create(
            crop='paddy',
            region='Vijayawada',
            price_per_quintal=2200.0,
            date=date.today(),
            is_peak_season=False
        )
        self.assertIsInstance(price, MarketPrice)
        self.assertEqual(price.price_per_quintal, 2200.0)
