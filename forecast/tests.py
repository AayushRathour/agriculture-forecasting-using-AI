"""
Unit tests for Bhoomi Puthra - Agricultural Forecasting System
Tests for yield calculation, price calculation, and recommendation logic
"""

from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from .models import (
    Farmer, DiseaseRecord, WeatherData, MarketPrice, PredictionResult
)
from .views import (
    calculate_yield_loss,
    calculate_selling_recommendation,
    predict_market_price
)


# ========================================
# Test Cases for Yield Calculation
# ========================================

class YieldCalculationTests(TestCase):
    """Test cases for yield loss calculation based on disease severity"""
    
    def test_low_severity_yield_loss(self):
        """Test that low severity disease results in 5% yield loss"""
        yield_loss = calculate_yield_loss('low')
        self.assertEqual(yield_loss, 5.0)
    
    def test_medium_severity_yield_loss(self):
        """Test that medium severity disease results in 15% yield loss"""
        yield_loss = calculate_yield_loss('medium')
        self.assertEqual(yield_loss, 15.0)
    
    def test_high_severity_yield_loss(self):
        """Test that high severity disease results in 30% yield loss"""
        yield_loss = calculate_yield_loss('high')
        self.assertEqual(yield_loss, 30.0)
    
    def test_invalid_severity_returns_zero(self):
        """Test that invalid severity returns 0% yield loss"""
        yield_loss = calculate_yield_loss('invalid')
        self.assertEqual(yield_loss, 0.0)
    
    def test_case_insensitive_severity(self):
        """Test that severity is case-insensitive"""
        self.assertEqual(calculate_yield_loss('LOW'), 5.0)
        self.assertEqual(calculate_yield_loss('Medium'), 15.0)
        self.assertEqual(calculate_yield_loss('HIGH'), 30.0)
    
    def test_empty_severity_string(self):
        """Test that empty string returns 0% yield loss"""
        yield_loss = calculate_yield_loss('')
        self.assertEqual(yield_loss, 0.0)


# ========================================
# Test Cases for Price Calculation
# ========================================

class PriceCalculationTests(TestCase):
    """Test cases for market price calculations and predictions"""
    
    def setUp(self):
        """Set up test data for market prices"""
        # Create sample market price data
        self.test_date = date(2023, 10, 15)
        
        MarketPrice.objects.create(
            crop='paddy',
            region='Krishna District',
            price_per_quintal=1407.00,
            date=self.test_date,
            is_peak_season=False
        )
        
        MarketPrice.objects.create(
            crop='turmeric',
            region='Krishna District',
            price_per_quintal=10655.00,
            date=self.test_date,
            is_peak_season=True
        )
    
    def test_current_market_price_retrieval(self):
        """Test that current market price is retrieved correctly"""
        paddy_price = MarketPrice.objects.get(crop='paddy')
        self.assertEqual(paddy_price.price_per_quintal, 1407.00)
    
    def test_peak_season_indicator(self):
        """Test that peak season is correctly identified"""
        turmeric_price = MarketPrice.objects.get(crop='turmeric')
        self.assertTrue(turmeric_price.is_peak_season)
        
        paddy_price = MarketPrice.objects.get(crop='paddy')
        self.assertFalse(paddy_price.is_peak_season)
    
    def test_price_display_format(self):
        """Test that price is formatted correctly"""
        paddy_price = MarketPrice.objects.get(crop='paddy')
        expected_str = f"Paddy (Rice) - Krishna District - ₹{paddy_price.price_per_quintal}/Q ({self.test_date})"
        self.assertEqual(str(paddy_price), expected_str)
    
    def test_profit_percentage_calculation(self):
        """Test profit percentage calculation in PredictionResult model"""
        # Create a test farmer
        farmer = Farmer.objects.create(
            mandal='machilipatnam',
            village='Test Village',
            crop='paddy',
            acres=5.0,
            sowing_date=date(2023, 6, 1),
            cold_storage=True,
            urgent_cash=False
        )
        
        # Create prediction result
        prediction = PredictionResult.objects.create(
            farmer=farmer,
            predicted_yield=100.0,
            yield_reduction_percentage=10.0,
            current_market_price=1407.00,
            total_current_value=140700.00,
            predicted_peak_price=1600.00,
            total_future_value=160000.00,
            profit_delta=19300.00,
            recommendation='store',
            recommendation_reason='Test reason',
            confidence_score=85.0
        )
        
        expected_percentage = round((19300.00 / 140700.00) * 100, 2)
        self.assertEqual(prediction.profit_percentage(), expected_percentage)
    
    def test_profit_percentage_with_zero_current_value(self):
        """Test that profit percentage returns 0 when current value is 0"""
        farmer = Farmer.objects.create(
            mandal='gudivada',
            village='Test Village 2',
            crop='mango',
            acres=2.0,
            sowing_date=date(2023, 7, 1),
            cold_storage=False,
            urgent_cash=True
        )
        
        prediction = PredictionResult.objects.create(
            farmer=farmer,
            predicted_yield=0.0,
            yield_reduction_percentage=100.0,
            current_market_price=2000.00,
            total_current_value=0.0,
            predicted_peak_price=2500.00,
            total_future_value=0.0,
            profit_delta=0.0,
            recommendation='sell',
            recommendation_reason='No yield',
            confidence_score=95.0
        )
        
        self.assertEqual(prediction.profit_percentage(), 0)


# ========================================
# Test Cases for Recommendation Logic
# ========================================

class RecommendationLogicTests(TestCase):
    """Test cases for selling recommendation logic"""
    
    def test_urgent_cash_recommends_sell(self):
        """Test that urgent cash need always recommends SELL"""
        result = calculate_selling_recommendation(
            predicted_yield=100.0,
            current_price=1500.0,
            peak_price=1800.0,
            cold_storage_available=True,
            urgent_cash_needed=True,
            profit_threshold=1000
        )
        
        self.assertEqual(result['recommendation'], 'SELL')
        self.assertIn('Urgent cash', result['reason'])
    
    def test_cold_storage_with_high_profit_recommends_store(self):
        """Test that cold storage + high profit recommends STORE"""
        result = calculate_selling_recommendation(
            predicted_yield=200.0,
            current_price=1000.0,
            peak_price=1500.0,
            cold_storage_available=True,
            urgent_cash_needed=False,
            profit_threshold=5000
        )
        
        self.assertEqual(result['recommendation'], 'STORE')
        self.assertIn('Cold storage available', result['reason'])
        self.assertTrue(result['is_profitable_to_store'])
    
    def test_cold_storage_with_low_profit_recommends_sell(self):
        """Test that cold storage + low profit recommends SELL"""
        result = calculate_selling_recommendation(
            predicted_yield=50.0,
            current_price=1000.0,
            peak_price=1050.0,
            cold_storage_available=True,
            urgent_cash_needed=False,
            profit_threshold=5000
        )
        
        self.assertEqual(result['recommendation'], 'SELL')
        self.assertIn('Storage costs', result['reason'])
        self.assertFalse(result['is_profitable_to_store'])
    
    def test_no_cold_storage_recommends_sell(self):
        """Test that no cold storage always recommends SELL"""
        result = calculate_selling_recommendation(
            predicted_yield=150.0,
            current_price=2000.0,
            peak_price=3000.0,
            cold_storage_available=False,
            urgent_cash_needed=False,
            profit_threshold=1000
        )
        
        self.assertEqual(result['recommendation'], 'SELL')
        self.assertIn('No cold storage', result['reason'])
    
    def test_profit_calculations_accuracy(self):
        """Test that profit calculations are accurate"""
        predicted_yield = 100.0
        current_price = 1200.0
        peak_price = 1500.0
        
        result = calculate_selling_recommendation(
            predicted_yield=predicted_yield,
            current_price=current_price,
            peak_price=peak_price,
            cold_storage_available=True,
            urgent_cash_needed=False,
            profit_threshold=1000
        )
        
        # Verify basic calculations
        expected_current_value = predicted_yield * current_price
        expected_future_value = predicted_yield * peak_price
        expected_profit_delta = expected_future_value - expected_current_value
        
        self.assertEqual(result['total_current_value'], expected_current_value)
        self.assertEqual(result['total_future_value'], expected_future_value)
        self.assertEqual(result['profit_delta'], expected_profit_delta)
    
    def test_storage_cost_calculation(self):
        """Test that storage costs are calculated correctly (5% of current value)"""
        result = calculate_selling_recommendation(
            predicted_yield=100.0,
            current_price=1000.0,
            peak_price=1200.0,
            cold_storage_available=True,
            urgent_cash_needed=False,
            profit_threshold=1000
        )
        
        expected_storage_cost = (100.0 * 1000.0) * 0.05  # 5% of current value
        self.assertEqual(result['storage_cost_estimate'], expected_storage_cost)
    
    def test_net_profit_after_storage(self):
        """Test that net profit after storage is calculated correctly"""
        result = calculate_selling_recommendation(
            predicted_yield=100.0,
            current_price=1000.0,
            peak_price=1300.0,
            cold_storage_available=True,
            urgent_cash_needed=False,
            profit_threshold=1000
        )
        
        profit_delta = (100.0 * 1300.0) - (100.0 * 1000.0)
        storage_cost = (100.0 * 1000.0) * 0.05
        expected_net_profit = profit_delta - storage_cost
        
        self.assertEqual(result['net_profit_after_storage'], expected_net_profit)
    
    def test_break_even_price_calculation(self):
        """Test that break-even price is calculated correctly"""
        predicted_yield = 100.0
        current_price = 1000.0
        
        result = calculate_selling_recommendation(
            predicted_yield=predicted_yield,
            current_price=current_price,
            peak_price=1200.0,
            cold_storage_available=True,
            urgent_cash_needed=False,
            profit_threshold=1000
        )
        
        storage_cost = result['storage_cost_estimate']
        expected_break_even = current_price + (storage_cost / predicted_yield)
        
        self.assertEqual(result['break_even_price'], expected_break_even)
    
    def test_zero_yield_handles_gracefully(self):
        """Test that zero yield is handled without errors"""
        result = calculate_selling_recommendation(
            predicted_yield=0.0,
            current_price=1000.0,
            peak_price=1200.0,
            cold_storage_available=False,
            urgent_cash_needed=True,
            profit_threshold=1000
        )
        
        self.assertEqual(result['total_current_value'], 0.0)
        self.assertEqual(result['total_future_value'], 0.0)
        self.assertEqual(result['profit_delta'], 0.0)
        self.assertEqual(result['break_even_price'], 0.0)


# ========================================
# Integration Tests
# ========================================

class IntegrationTests(TestCase):
    """Integration tests combining models and calculations"""
    
    def setUp(self):
        """Set up test data"""
        # Create a farmer
        self.farmer = Farmer.objects.create(
            mandal='machilipatnam',
            village='Test Village',
            crop='paddy',
            acres=10.0,
            sowing_date=date.today() - timedelta(days=60),
            cold_storage=True,
            urgent_cash=False
        )
        
        # Create weather data
        WeatherData.objects.create(
            mandal='machilipatnam',
            date=date.today(),
            temperature=28.5,
            rainfall=25.0,
            humidity=75.0
        )
        
        # Create market price
        MarketPrice.objects.create(
            crop='paddy',
            region='Krishna District',
            price_per_quintal=1407.00,
            date=date.today(),
            is_peak_season=False
        )
    
    def test_farmer_crop_age_calculation(self):
        """Test that farmer's crop age is calculated correctly"""
        expected_age = (date.today() - self.farmer.sowing_date).days
        self.assertEqual(self.farmer.crop_age_days(), expected_age)
    
    def test_complete_prediction_workflow(self):
        """Test complete prediction workflow with real data"""
        # Create disease record
        disease = DiseaseRecord.objects.create(
            farmer=self.farmer,
            disease_name='Leaf Blight',
            severity='medium',
            yield_loss_percentage=15.0,
            notes='Test disease'
        )
        
        # Calculate yield with disease impact
        base_yield = self.farmer.acres * 20  # Assume 20 quintals per acre
        yield_loss = calculate_yield_loss(disease.severity)
        predicted_yield = base_yield * (1 - yield_loss / 100)
        
        self.assertGreater(predicted_yield, 0)
        self.assertLess(predicted_yield, base_yield)
        
        # Get current price
        current_price = MarketPrice.objects.get(crop='paddy').price_per_quintal
        
        # Calculate recommendation
        recommendation = calculate_selling_recommendation(
            predicted_yield=predicted_yield,
            current_price=current_price,
            peak_price=current_price * 1.15,  # 15% increase
            cold_storage_available=self.farmer.cold_storage,
            urgent_cash_needed=self.farmer.urgent_cash,
            profit_threshold=5000
        )
        
        self.assertIn(recommendation['recommendation'], ['SELL', 'STORE'])
        self.assertGreater(recommendation['total_current_value'], 0)
    
    def test_model_relationships(self):
        """Test that model relationships work correctly"""
        # Create disease record
        disease = DiseaseRecord.objects.create(
            farmer=self.farmer,
            disease_name='Brown Spot',
            severity='low',
            yield_loss_percentage=5.0
        )
        
        # Create prediction result
        prediction = PredictionResult.objects.create(
            farmer=self.farmer,
            predicted_yield=180.0,
            yield_reduction_percentage=10.0,
            current_market_price=1407.00,
            total_current_value=253260.00,
            predicted_peak_price=1600.00,
            total_future_value=288000.00,
            profit_delta=34740.00,
            recommendation='store',
            recommendation_reason='Profitable to wait',
            confidence_score=85.0
        )
        
        # Test reverse relationships
        self.assertEqual(self.farmer.diseases.count(), 1)
        self.assertEqual(self.farmer.prediction, prediction)
        self.assertEqual(prediction.farmer, self.farmer)


# ========================================
# Edge Cases and Error Handling
# ========================================

class EdgeCaseTests(TestCase):
    """Test edge cases and error handling"""
    
    def test_negative_yield_handled(self):
        """Test that negative yield values are handled properly"""
        # This should not happen in production, but test defensively
        result = calculate_selling_recommendation(
            predicted_yield=-10.0,
            current_price=1000.0,
            peak_price=1200.0,
            cold_storage_available=True,
            urgent_cash_needed=False,
            profit_threshold=1000
        )
        
        # Should still calculate but values will be negative
        self.assertIsNotNone(result['recommendation'])
    
    def test_very_high_profit_threshold(self):
        """Test with unrealistically high profit threshold"""
        result = calculate_selling_recommendation(
            predicted_yield=100.0,
            current_price=1000.0,
            peak_price=1200.0,
            cold_storage_available=True,
            urgent_cash_needed=False,
            profit_threshold=1000000  # Very high threshold
        )
        
        self.assertEqual(result['recommendation'], 'SELL')
        self.assertFalse(result['is_profitable_to_store'])
    
    def test_equal_current_and_peak_prices(self):
        """Test when current price equals peak price"""
        result = calculate_selling_recommendation(
            predicted_yield=100.0,
            current_price=1500.0,
            peak_price=1500.0,  # Same as current
            cold_storage_available=True,
            urgent_cash_needed=False,
            profit_threshold=1000
        )
        
        self.assertEqual(result['profit_delta'], 0.0)
        self.assertEqual(result['recommendation'], 'SELL')
