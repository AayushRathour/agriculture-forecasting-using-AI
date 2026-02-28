"""
Views for the forecast app
Handles all the logic for crop forecasting system with ML/AI models
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.utils import timezone
from django.db import models
from .models import (
    Farmer, DiseaseRecord, WeatherData, MarketPrice, PredictionResult,
    CROP_CHOICES
)
from datetime import datetime, timedelta
from django.db.models import Count, Avg
import json
import random
import os

# Import ML models
from .ml_models.disease_detector import DiseaseDetector
from .ml_models.yield_predictor import YieldPredictor
from .ml_models.price_predictor import PricePredictor

# Initialize ML models (singleton pattern)
_disease_detector = None
_yield_predictor = None
_price_predictor = None

def get_disease_detector():
    """Get or create disease detector instance"""
    global _disease_detector
    if _disease_detector is None:
        _disease_detector = DiseaseDetector()
    return _disease_detector

def get_yield_predictor():
    """Get or create yield predictor instance"""
    global _yield_predictor
    if _yield_predictor is None:
        _yield_predictor = YieldPredictor()
    return _yield_predictor

def get_price_predictor():
    """Get or create price predictor instance"""
    global _price_predictor
    if _price_predictor is None:
        _price_predictor = PricePredictor()
    return _price_predictor


# ========================================
# Utility Functions
# ========================================

def calculate_yield_loss(severity):
    """
    Calculate yield loss percentage based on disease severity
    
    Args:
        severity (str): Disease severity level ('low', 'medium', 'high')
    
    Returns:
        float: Yield loss percentage (5, 15, or 30)
    """
    severity_map = {
        'low': 5.0,
        'medium': 15.0,
        'high': 30.0
    }
    return severity_map.get(severity.lower(), 0.0)


def calculate_selling_recommendation(predicted_yield, current_price, peak_price, 
                                    cold_storage_available, urgent_cash_needed, 
                                    profit_threshold=1000):
    """
    Calculate selling recommendation based on yield, prices, and farmer's situation
    
    Args:
        predicted_yield (float): Predicted crop yield in quintals
        current_price (float): Current market price per quintal
        peak_price (float): Predicted peak price per quintal
        cold_storage_available (bool): Does farmer have cold storage access?
        urgent_cash_needed (bool): Does farmer need urgent cash?
        profit_threshold (float): Minimum profit delta to recommend STORE (default: 1000 rupees)
    
    Returns:
        dict: Selling recommendation with financial breakdown
            - total_current_value: Total value at current price
            - total_future_value: Total value at peak price
            - profit_delta: Difference between future and current value
            - profit_percentage: Percentage gain by waiting
            - recommendation: 'SELL' or 'STORE'
            - reason: Explanation for recommendation
            - storage_cost_estimate: Estimated storage cost if STORE
            - net_profit_after_storage: Net profit after storage costs
    """
    
    # Step 1: Calculate total current value
    total_current_value = round(predicted_yield * current_price, 2)
    
    # Step 2: Calculate future value at peak price
    total_future_value = round(predicted_yield * peak_price, 2)
    
    # Step 3: Calculate profit delta
    profit_delta = round(total_future_value - total_current_value, 2)
    
    # Step 4: Calculate profit percentage
    if total_current_value > 0:
        profit_percentage = round((profit_delta / total_current_value) * 100, 2)
    else:
        profit_percentage = 0
    
    # Step 5: Estimate storage costs (approximately 2-3% of current value per month)
    # Assuming average 2 months storage period
    storage_cost_percentage = 5  # 2.5% per month × 2 months
    storage_cost_estimate = round(total_current_value * (storage_cost_percentage / 100), 2)
    
    # Step 6: Calculate net profit after storage costs
    net_profit_after_storage = round(profit_delta - storage_cost_estimate, 2)
    
    # Step 7: Make recommendation based on conditions
    recommendation = None
    reason = None
    
    # Priority 1: Urgent cash needed → SELL immediately
    if urgent_cash_needed:
        recommendation = 'SELL'
        reason = 'Urgent cash requirement. Immediate sale recommended despite potential future gains.'
    
    # Priority 2: Cold storage available and profit exceeds threshold → STORE
    elif cold_storage_available and net_profit_after_storage > profit_threshold:
        recommendation = 'STORE'
        reason = f'Cold storage available. Net profit after storage costs (₹{net_profit_after_storage:,.2f}) exceeds threshold. Wait for peak prices.'
    
    # Priority 3: Cold storage available but profit below threshold → SELL
    elif cold_storage_available and net_profit_after_storage <= profit_threshold:
        recommendation = 'SELL'
        reason = f'Storage costs (₹{storage_cost_estimate:,.2f}) reduce net profit below threshold. Sell now to avoid storage expenses.'
    
    # Priority 4: No cold storage → SELL (risk of spoilage)
    else:
        recommendation = 'SELL'
        reason = 'No cold storage available. Sell immediately to avoid spoilage and quality degradation.'
    
    # Step 8: Return structured dictionary
    return {
        'total_current_value': total_current_value,
        'total_future_value': total_future_value,
        'profit_delta': profit_delta,
        'profit_percentage': profit_percentage,
        'recommendation': recommendation,
        'reason': reason,
        'storage_cost_estimate': storage_cost_estimate,
        'net_profit_after_storage': net_profit_after_storage,
        'is_profitable_to_store': net_profit_after_storage > profit_threshold,
        'break_even_price': round(current_price + (storage_cost_estimate / predicted_yield), 2) if predicted_yield > 0 else 0
    }


def predict_market_price(crop_type, region='Vijayawada'):
    """
    Simple price prediction logic for Krishna District crops
    
    Args:
        crop_type (str): Type of crop (paddy, mango, cotton, etc.)
        region (str): Market region (default: 'Vijayawada')
    
    Returns:
        dict: Price prediction results including:
            - current_price: Latest market price per quintal
            - predicted_peak_price: Expected peak price (10-15% increase)
            - increase_percentage: Percentage increase expected
            - best_selling_start: Start date of best selling window
            - best_selling_end: End date of best selling window
            - recommendation: Selling recommendation message
            - price_date: Date of the current price data
    """
    
    # Step 1: Fetch latest market price for the crop
    try:
        latest_price = MarketPrice.objects.filter(
            crop=crop_type.lower()
        ).order_by('-date').first()
        
        if not latest_price:
            # Use fallback prices so recommendation flow still works
            fallback_prices = {
                'paddy': 2200,
                'mango': 3200,
                'chillies': 9000,
                'cotton': 7200,
                'turmeric': 9500,
                'sugarcane': 350,
                'banana': 1800,
                'tomato': 1400,
                'okra': 2200,
                'brinjal': 2000,
                'maize': 2100,
                'groundnut': 6200,
                'sunflower': 6000,
                'tobacco': 7800,
            }
            current_price = float(fallback_prices.get(crop_type.lower(), 2500))
            price_date = datetime.now().date()
            using_fallback_price = True
        else:
            current_price = latest_price.price_per_quintal
            price_date = latest_price.date
            using_fallback_price = False
        
    except Exception as e:
        return {
            'current_price': 0,
            'predicted_peak_price': 0,
            'increase_percentage': 0,
            'best_selling_start': None,
            'best_selling_end': None,
            'recommendation': f'Error fetching market data: {str(e)}',
            'price_date': None,
            'error': True
        }
    
    # Step 2: Calculate predicted peak price (10-15% increase)
    # Use a random value between 10-15% for realistic variation
    increase_percentage = round(random.uniform(10, 15), 1)
    predicted_peak_price = round(current_price * (1 + increase_percentage / 100), 2)
    
    # Step 3: Suggest selling window based on current month
    current_date = datetime.now()
    current_month = current_date.month
    
    # Peak harvest seasons for different crops in Krishna District
    # Format: {crop: [(start_month, end_month), ...]}
    harvest_seasons = {
        'paddy': [(11, 1), (5, 7)],      # November-January, May-July
        'mango': [(4, 6)],                # April-June
        'chillies': [(2, 3), (11, 12)],  # February-March, November-December
        'cotton': [(11, 2)],              # November-February
        'turmeric': [(1, 3)],             # January-March
        'sugarcane': [(12, 3)],           # December-March
        'banana': [(1, 12)],              # Year-round
        'tomato': [(11, 2), (6, 8)],     # November-February, June-August
        'okra': [(10, 2), (5, 7)],       # October-February, May-July
        'brinjal': [(11, 2), (6, 8)],    # November-February, June-August
        'maize': [(2, 4), (9, 11)],      # February-April, September-November
        'groundnut': [(9, 11)],           # September-November
        'sunflower': [(2, 4), (11, 12)], # February-April, November-December
        'tobacco': [(1, 3)],              # January-March
    }
    
    crop_seasons = harvest_seasons.get(crop_type.lower(), [(1, 12)])
    
    # Determine if currently in harvest season
    in_harvest_season = False
    for start_month, end_month in crop_seasons:
        if start_month <= end_month:
            # Normal range (e.g., April-June)
            if start_month <= current_month <= end_month:
                in_harvest_season = True
                break
        else:
            # Wraps around year end (e.g., November-January)
            if current_month >= start_month or current_month <= end_month:
                in_harvest_season = True
                break
    
    # Calculate selling window (30-45 days from now for best prices)
    # If in harvest season, suggest waiting; otherwise sell soon
    if in_harvest_season:
        # Currently harvest season - prices may be low, suggest waiting
        days_to_wait = random.randint(30, 45)
        best_selling_start = current_date + timedelta(days=days_to_wait)
        best_selling_end = best_selling_start + timedelta(days=14)  # 2-week window
        recommendation = f"Currently harvest season. Wait {days_to_wait} days for better prices (off-season premium)."
    else:
        # Off-season - prices likely better, can sell sooner
        days_to_sell = random.randint(7, 14)
        best_selling_start = current_date + timedelta(days=days_to_sell)
        best_selling_end = best_selling_start + timedelta(days=10)
        recommendation = f"Good time to sell! Off-season prices are favorable. Sell within {days_to_sell}-{days_to_sell+10} days."
    
    if using_fallback_price:
        recommendation = (
            recommendation +
            " Market price is estimated due to unavailable mandi data for this crop."
        )

    # Step 4: Return complete prediction
    return {
        'current_price': round(current_price, 2),
        'predicted_peak_price': predicted_peak_price,
        'increase_percentage': increase_percentage,
        'best_selling_start': best_selling_start.date(),
        'best_selling_end': best_selling_end.date(),
        'recommendation': recommendation,
        'price_date': price_date,
        'error': False
    }


def predict_crop_yield(crop_type, acres, rainfall, temperature, humidity, disease_severity='low'):
    """
    Simple yield prediction logic for Krishna District crops
    
    Args:
        crop_type (str): Type of crop (paddy, mango, cotton, etc.)
        acres (float): Land area in acres
        rainfall (float): Rainfall in mm
        temperature (float): Temperature in Celsius
        humidity (float): Humidity percentage (0-100)
        disease_severity (str): Disease severity level ('low', 'medium', 'high')
    
    Returns:
        dict: Prediction results with breakdown
            - predicted_yield: Final yield in quintals
            - base_yield: Base yield before adjustments
            - weather_factor: Weather adjustment factor (0.5 to 1.2)
            - disease_loss_percent: Disease loss percentage
            - explanation: Human-readable explanation
    """
    
    # Step 1: Base yield per acre for each crop (in quintals)
    # Based on average Krishna District yields
    BASE_YIELD_PER_ACRE = {
        'paddy': 25.0,          # Rice - 25 quintals/acre
        'mango': 30.0,          # Mango - 30 quintals/acre
        'chillies': 12.0,       # Chillies - 12 quintals/acre
        'cotton': 8.0,          # Cotton - 8 quintals/acre
        'turmeric': 20.0,       # Turmeric - 20 quintals/acre
        'sugarcane': 250.0,     # Sugarcane - 250 quintals/acre
        'banana': 150.0,        # Banana - 150 quintals/acre
        'tomato': 100.0,        # Tomato - 100 quintals/acre
        'okra': 40.0,           # Okra - 40 quintals/acre
        'brinjal': 80.0,        # Brinjal - 80 quintals/acre
        'maize': 15.0,          # Maize - 15 quintals/acre
        'groundnut': 10.0,      # Groundnut - 10 quintals/acre
        'sunflower': 8.0,       # Sunflower - 8 quintals/acre
        'tobacco': 12.0,        # Tobacco - 12 quintals/acre
    }
    
    crop_key = crop_type.lower()
    base_yield_per_acre = BASE_YIELD_PER_ACRE.get(crop_key, 15.0)  # Default 15 quintals
    base_total_yield = base_yield_per_acre * acres
    
    # Step 2: Weather adjustment factor (ranges from 0.5 to 1.2)
    # Optimal ranges for Krishna District crops
    rainfall_factor = 1.0
    temperature_factor = 1.0
    humidity_factor = 1.0
    
    # Rainfall impact (optimal: 600-1200mm annually, roughly 50-100mm monthly)
    if rainfall < 30:           # Too dry
        rainfall_factor = 0.6
    elif rainfall < 50:         # Below optimal
        rainfall_factor = 0.8
    elif rainfall <= 100:       # Optimal range
        rainfall_factor = 1.1
    elif rainfall <= 150:       # Good but high
        rainfall_factor = 1.0
    else:                       # Excessive rainfall
        rainfall_factor = 0.7
    
    # Temperature impact (optimal: 25-35°C for most crops)
    if temperature < 15:        # Too cold
        temperature_factor = 0.6
    elif temperature < 20:      # Cool
        temperature_factor = 0.8
    elif temperature <= 35:     # Optimal range
        temperature_factor = 1.1
    elif temperature <= 40:     # Hot but manageable
        temperature_factor = 0.9
    else:                       # Too hot
        temperature_factor = 0.7
    
    # Humidity impact (optimal: 60-80%)
    if humidity < 40:           # Too dry
        humidity_factor = 0.8
    elif humidity < 60:         # Slightly dry
        humidity_factor = 0.9
    elif humidity <= 80:        # Optimal range
        humidity_factor = 1.1
    elif humidity <= 90:        # High humidity
        humidity_factor = 0.95
    else:                       # Excessive humidity (disease risk)
        humidity_factor = 0.8
    
    # Combined weather factor (average of three factors, capped between 0.5 and 1.2)
    weather_factor = (rainfall_factor + temperature_factor + humidity_factor) / 3
    weather_factor = max(0.5, min(1.2, weather_factor))
    
    # Step 3: Apply weather adjustment
    yield_after_weather = base_total_yield * weather_factor
    
    # Step 4: Calculate and apply disease loss
    disease_loss_percent = calculate_yield_loss(disease_severity)
    disease_loss_amount = yield_after_weather * (disease_loss_percent / 100)
    
    # Step 5: Final predicted yield
    final_yield = yield_after_weather - disease_loss_amount
    final_yield = max(0, final_yield)  # Ensure non-negative
    
    # Step 6: Generate explanation
    explanation = f"""
Yield Prediction Breakdown:
- Base Yield: {base_yield_per_acre} quintals/acre × {acres} acres = {base_total_yield:.2f} quintals
- Weather Factor: {weather_factor:.2f}x (Rainfall: {rainfall_factor:.2f}, Temp: {temperature_factor:.2f}, Humidity: {humidity_factor:.2f})
- After Weather: {yield_after_weather:.2f} quintals
- Disease Loss: {disease_loss_percent}% = {disease_loss_amount:.2f} quintals
- Final Predicted Yield: {final_yield:.2f} quintals
    """.strip()
    
    return {
        'predicted_yield': round(final_yield, 2),
        'base_yield': round(base_total_yield, 2),
        'weather_factor': round(weather_factor, 2),
        'disease_loss_percent': disease_loss_percent,
        'disease_loss_amount': round(disease_loss_amount, 2),
        'yield_after_weather': round(yield_after_weather, 2),
        'explanation': explanation
    }


def home(request):
    """
    Home page view - Landing page with feature overview
    """
    context = {
        'page': 'home'
    }
    
    # Add user stats for authenticated users
    if request.user.is_authenticated:
        from .models import PriceAlert, FavoriteCrop, Notification
        
        context['total_submissions'] = Farmer.objects.filter(user=request.user).count()
        context['active_alerts'] = PriceAlert.objects.filter(user=request.user, is_active=True, is_triggered=False).count()
        context['favorite_crops_count'] = FavoriteCrop.objects.filter(user=request.user).count()
        context['unread_notifications'] = Notification.objects.filter(user=request.user, is_read=False).count()
    
    return render(request, 'forecast/home.html', context)


def input_form(request):
    """
    Input form view - Where farmers enter crop details
    Will be implemented in next step
    """
    context = {
        'page': 'input'
    }
    return render(request, 'forecast/input_form.html', context)


@login_required(login_url='/login/')
def result(request):
    """
    Result view - Shows forecast results after farmer submission
    Uses ML models for predictions
    """
    farmer_id = request.session.get('farmer_id')
    
    if not farmer_id:
        messages.warning(request, 'Please submit farmer data first.')
        return redirect('forecast:farmer_input')
    
    try:
        farmer = Farmer.objects.get(id=farmer_id)
        disease_record = DiseaseRecord.objects.filter(farmer=farmer).first()
        
        # Get weather data for yield prediction
        weather_data = WeatherData.objects.filter(mandal=farmer.mandal).order_by('-date').first()
        
        # Set default weather values if no data available
        rainfall = weather_data.rainfall if weather_data else 75.0
        temperature = weather_data.temperature if weather_data else 28.0
        humidity = weather_data.humidity if weather_data else 70.0
        
        # Get disease information
        disease_severity = disease_record.severity if disease_record else 'low'
        disease_yield_loss = disease_record.yield_loss_percentage if disease_record else 0
        
        # Calculate crop age
        crop_age_days = farmer.crop_age_days()
        
        # === ML-BASED YIELD PREDICTION ===
        yield_predictor = get_yield_predictor()
        yield_prediction = yield_predictor.predict(
            crop_type=farmer.crop,
            acres=farmer.acres,
            rainfall=rainfall,
            temperature=temperature,
            humidity=humidity,
            disease_severity=disease_severity,
            disease_yield_loss=disease_yield_loss,
            crop_age_days=crop_age_days,
            soil_quality='medium',  # Default, can be added to form
            irrigation='moderate'   # Default, can be added to form
        )
        
        # === ML-BASED PRICE PREDICTION ===
        # Get current price from database
        latest_price = MarketPrice.objects.filter(
            crop=farmer.crop.lower()
        ).order_by('-date').first()
        
        current_price = latest_price.price_per_quintal if latest_price else None
        
        price_predictor = get_price_predictor()
        price_prediction = price_predictor.predict(
            crop_type=farmer.crop,
            current_price=current_price,
            region='Vijayawada',
            supply_level='normal',  # Can be enhanced with real data
            demand_level='normal'   # Can be enhanced with real data
        )
        
        # === SELLING RECOMMENDATION ===
        selling_recommendation = None
        if yield_prediction and price_prediction:
            selling_recommendation = calculate_selling_recommendation(
                predicted_yield=yield_prediction['predicted_yield'],
                current_price=price_prediction['current_price'],
                peak_price=price_prediction['predicted_peak_price'],
                cold_storage_available=farmer.cold_storage,
                urgent_cash_needed=farmer.urgent_cash
            )
        
        # === SAVE PREDICTION RESULT ===
        if yield_prediction and price_prediction and selling_recommendation:
            # Parse peak price date
            peak_date = None
            if price_prediction.get('best_selling_start'):
                try:
                    start_value = price_prediction['best_selling_start']
                    if isinstance(start_value, datetime):
                        peak_date = start_value.date()
                    elif isinstance(start_value, str):
                        peak_date = datetime.strptime(start_value, '%Y-%m-%d').date()
                    else:
                        peak_date = start_value
                except Exception:
                    peak_date = None
            
            # Calculate yield reduction percentage
            yield_reduction = 0
            if yield_prediction.get('base_yield', 0) > 0:
                yield_reduction = ((yield_prediction['base_yield'] - yield_prediction['predicted_yield']) / yield_prediction['base_yield']) * 100
            
            # Calculate confidence score
            base_confidence = yield_prediction.get('confidence', 70.0)
            if weather_data:
                base_confidence = min(base_confidence + 5.0, 95.0)
            if disease_record:
                base_confidence = min(base_confidence + 5.0, 95.0)
            
            # Create or update PredictionResult
            prediction_result, created = PredictionResult.objects.update_or_create(
                farmer=farmer,
                defaults={
                    'predicted_yield': yield_prediction['predicted_yield'],
                    'yield_reduction_percentage': round(yield_reduction, 2),
                    'current_market_price': price_prediction['current_price'],
                    'total_current_value': selling_recommendation['total_current_value'],
                    'predicted_peak_price': price_prediction['predicted_peak_price'],
                    'peak_price_date': peak_date,
                    'total_future_value': selling_recommendation['total_future_value'],
                    'profit_delta': selling_recommendation['profit_delta'],
                    'recommendation': selling_recommendation['recommendation'],
                    'recommendation_reason': selling_recommendation['reason'],
                    'confidence_score': base_confidence,
                }
            )
        
        context = {
            'page': 'result',
            'farmer': farmer,
            'disease_record': disease_record,
            'price_prediction': price_prediction,
            'yield_prediction': yield_prediction,
            'selling_recommendation': selling_recommendation,
            'weather_data': weather_data,
        }
        
        return render(request, 'forecast/result.html', context)
        
    except Farmer.DoesNotExist:
        messages.error(request, 'Farmer record not found.')
        return redirect('forecast:farmer_input')


@login_required(login_url='/login/')
def farmer_input(request):
    """
    Farmer input form page with language toggle
    Handles farmer data submission with image upload, validation, and error handling
    """
    if request.method == 'POST':
        try:
            # Get and validate required form fields
            mandal = request.POST.get('mandal', '').strip()
            village = request.POST.get('village', '').strip()
            crop = request.POST.get('crop', '').strip()
            acres_str = request.POST.get('acres', '').strip()
            sowing_date = request.POST.get('sowing_date', '').strip()
            
            # Validate required fields
            if not all([mandal, village, crop, acres_str, sowing_date]):
                messages.error(request, 'All required fields must be filled out.')
                return redirect('forecast:farmer_input')
            
            # Validate and convert acres to float
            try:
                acres = float(acres_str)
                if acres <= 0:
                    messages.error(request, 'Acres must be a positive number.')
                    return redirect('forecast:farmer_input')
            except ValueError:
                messages.error(request, 'Invalid acres value. Please enter a valid number.')
                return redirect('forecast:farmer_input')
            
            # Validate date format
            try:
                datetime.strptime(sowing_date, '%Y-%m-%d')
            except ValueError:
                messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
                return redirect('forecast:farmer_input')
            
            # Get optional boolean fields
            cold_storage = request.POST.get('cold_storage') == 'true'
            urgent_cash = request.POST.get('urgent_cash') == 'true'
            
            # Get optional crop image
            crop_image = request.FILES.get('crop_image')
            
            # Create Farmer record
            farmer = Farmer.objects.create(
                user=request.user if request.user.is_authenticated else None,
                mandal=mandal,
                village=village,
                crop=crop,
                acres=acres,
                sowing_date=sowing_date,
                cold_storage=cold_storage,
                urgent_cash=urgent_cash
            )
            
            # Create DiseaseRecord if image uploaded
            if crop_image:
                # Validate image file
                valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
                file_extension = crop_image.name.split('.')[-1].lower()
                
                if file_extension not in valid_extensions:
                    # Delete the farmer record if image is invalid
                    farmer.delete()
                    messages.error(request, 'Invalid image format. Please upload JPG, JPEG, PNG, or GIF.')
                    return redirect('forecast:farmer_input')
                
                # First save the image temporarily to analyze it
                disease_record = DiseaseRecord.objects.create(
                    farmer=farmer,
                    image=crop_image,
                    severity='low',  # Will be updated by ML model
                    yield_loss_percentage=0,  # Will be updated by ML model
                    detection_date=datetime.now(),
                    disease_name='Analyzing...'
                )
                
                # Use ML model to detect disease
                try:
                    detector = get_disease_detector()
                    detection_result = detector.predict(
                        disease_record.image.path,
                        crop_type=crop
                    )
                    
                    # Update disease record with ML predictions
                    disease_record.disease_name = detection_result['disease_name']
                    disease_record.severity = detection_result['severity']
                    disease_record.yield_loss_percentage = detection_result['yield_loss']
                    disease_record.notes = (
                        f"ML Detection (Confidence: {detection_result['confidence']:.1f}%)\n"
                        f"Method: {detection_result['method']}\n"
                        f"Detected: {detection_result['disease_name']}"
                    )
                    disease_record.save()
                    
                except Exception as e:
                    # Fall back to manual severity if ML fails
                    severity = request.POST.get('severity', 'medium').lower()
                    if severity not in ['low', 'medium', 'high']:
                        severity = 'medium'
                    
                    disease_record.severity = severity
                    disease_record.yield_loss_percentage = calculate_yield_loss(severity)
                    disease_record.disease_name = 'Unknown (ML Analysis Failed)'
                    disease_record.notes = f'ML detection error: {str(e)}'
                    disease_record.save()
            
            messages.success(request, 'Farmer data submitted successfully! Analyzing your crop...')
            
            # Store farmer ID in session for result page
            request.session['farmer_id'] = farmer.id
            
            return redirect('forecast:result')
            
        except Exception as e:
            messages.error(request, f'Error submitting data: {str(e)}')
            return redirect('forecast:farmer_input')
    
    # GET request - Display form
    # Context data for form
    villages_dict = {
        'Machilipatnam': ['Chilakalapudi', 'Avanigadda', 'Koduru', 'Nagayalanka'],
        'Gudivada': ['Gudivada Urban', 'Gudivada Rural', 'Mudinepalli', 'Pedapalem'],
        'Vuyyur': ['Vuyyuru Urban', 'Vuyyuru Rural', 'Jaggaiahpeta', 'Nandivada']
    }
    
    context = {
        'mandals': ['Machilipatnam', 'Gudivada', 'Vuyyur'],
        'villages': json.dumps(villages_dict),
        'crops': [
            ('paddy', 'Paddy'),
            ('cotton', 'Cotton'),
            ('chillies', 'Chillies'),
            ('turmeric', 'Turmeric'),
            ('maize', 'Maize'),
            ('sugarcane', 'Sugarcane'),
            ('banana', 'Banana'),
            ('groundnut', 'Groundnut'),
            ('sunflower', 'Sunflower'),
            ('tobacco', 'Tobacco')
        ]
    }
    
    return render(request, 'forecast/farmer_input.html', context)


# Admin check function
def is_admin(user):
    return user.is_authenticated and user.is_staff


# Admin Login View
def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('forecast:admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f'Welcome Admin {user.username}!')
            return redirect('forecast:admin_dashboard')
        else:
            messages.error(request, 'Invalid admin credentials or insufficient permissions.')
    
    return render(request, 'forecast/admin_login.html')


# Admin Register View
def admin_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        admin_secret = request.POST.get('admin_secret')
        
        # Simple secret key check (you can change this)
        admin_secret = request.POST.get('admin_secret')
        expected_secret = os.environ.get('ADMIN_SECRET_KEY', 'AGRI2026')
        
        if admin_secret != expected_secret:
            messages.error(request, 'Invalid admin secret key!')
            return render(request, 'forecast/admin_register.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'forecast/admin_register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return render(request, 'forecast/admin_register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return render(request, 'forecast/admin_register.html')
        
        # Create admin user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_staff = True
        user.save()
        
        messages.success(request, 'Admin account created successfully! Please login.')
        return redirect('forecast:admin_login')
    
    return render(request, 'forecast/admin_register.html')


# ========================================
# ENHANCED USER FEATURES
# ========================================

@login_required(login_url='/login/')
def crop_comparison(request):
    """Compare multiple crops performance for the user - Optimized version"""
    from django.db.models import Avg, Sum, Count, Q
    import json
    
    # Optimized query - fetch all user's farmer records with predictions in one go
    user_farmers = Farmer.objects.filter(user=request.user).select_related('user')
    
    if not user_farmers.exists():
        context = {
            'comparison_data': [],
            'chart_json': json.dumps({'labels': [], 'yields': [], 'profits': []}),
        }
        return render(request, 'forecast/crop_comparison.html', context)
    
    # Get predictions with select_related to minimize queries
    farmer_ids = list(user_farmers.values_list('id', flat=True))
    predictions = PredictionResult.objects.filter(
        farmer_id__in=farmer_ids
    ).select_related('farmer')
    
    # Group data by crop
    crop_data = {}
    for farmer in user_farmers:
        crop = farmer.crop
        if crop not in crop_data:
            crop_data[crop] = {
                'farmers': [],
                'predictions': []
            }
        crop_data[crop]['farmers'].append(farmer)
    
    for prediction in predictions:
        crop = prediction.farmer.crop
        if crop in crop_data:
            crop_data[crop]['predictions'].append(prediction)
    
    # Calculate statistics
    comparison_data = []
    for crop, data in crop_data.items():
        farmers_list = data['farmers']
        predictions_list = data['predictions']
        
        total_acres = sum(f.acres for f in farmers_list)
        total_yield = sum(p.predicted_yield for p in predictions_list) if predictions_list else 0
        avg_yield = total_yield / len(predictions_list) if predictions_list else 0
        
        total_current_value = sum(p.total_current_value for p in predictions_list if p.total_current_value) if predictions_list else 0
        avg_current_value = total_current_value / len(predictions_list) if predictions_list else 0
        
        total_profit = sum(p.profit_delta for p in predictions_list if p.profit_delta) if predictions_list else 0
        
        stats = {
            'crop': crop,
            'crop_display': dict(CROP_CHOICES).get(crop, crop),
            'total_submissions': len(farmers_list),
            'total_acres': total_acres,
            'avg_yield': avg_yield,
            'total_yield': total_yield,
            'avg_current_value': avg_current_value,
            'total_profit': total_profit,
        }
        comparison_data.append(stats)
    
    # Sort by total submissions (most active crops first)
    comparison_data.sort(key=lambda x: x['total_submissions'], reverse=True)
    
    # Chart data for visualization
    chart_data = {
        'labels': [item['crop_display'] for item in comparison_data],
        'yields': [round(float(item['avg_yield']), 2) for item in comparison_data],
        'profits': [round(float(item['total_profit']), 2) for item in comparison_data],
    }
    
    context = {
        'comparison_data': comparison_data,
        'chart_json': json.dumps(chart_data),
    }
    
    return render(request, 'forecast/crop_comparison.html', context)


@login_required(login_url='/login/')
def historical_analysis(request):
    """View historical trends and analysis for user's farming data - Optimized version"""
    from django.db.models import Avg, Sum
    from datetime import datetime, timedelta
    import json
    
    # Get data from last 12 months
    one_year_ago = timezone.now() - timedelta(days=365)
    
    # Optimized query - fetch all user's farmers with select_related
    user_farmers = Farmer.objects.filter(
        user=request.user,
        created_at__gte=one_year_ago
    ).select_related('user').order_by('created_at')
    
    if not user_farmers.exists():
        context = {
            'monthly_stats': {},
            'chart_json': json.dumps({'labels': [], 'submissions': [], 'acres': [], 'yields': []}),
        }
        return render(request, 'forecast/historical_analysis.html', context)
    
    # Fetch all predictions for these farmers in one query
    farmer_ids = list(user_farmers.values_list('id', flat=True))
    predictions_map = {}
    predictions = PredictionResult.objects.filter(farmer_id__in=farmer_ids).select_related('farmer')
    for pred in predictions:
        predictions_map[pred.farmer_id] = pred
    
    # Monthly statistics - optimized calculation
    monthly_stats = {}
    for farmer in user_farmers:
        month_key = farmer.created_at.strftime('%Y-%m')
        if month_key not in monthly_stats:
            monthly_stats[month_key] = {
                'submissions': 0,
                'total_acres': 0,
                'total_yield': 0,
            }
        monthly_stats[month_key]['submissions'] += 1
        monthly_stats[month_key]['total_acres'] += farmer.acres
        
        # Add yield if prediction exists (from pre-fetched map)
        prediction = predictions_map.get(farmer.id)
        if prediction:
            monthly_stats[month_key]['total_yield'] += prediction.predicted_yield
    
    # Prepare chart data
    months = sorted(monthly_stats.keys())
    chart_data = {
        'labels': months,
        'submissions': [monthly_stats[m]['submissions'] for m in months],
        'acres': [float(monthly_stats[m]['total_acres']) for m in months],
        'yields': [float(monthly_stats[m]['total_yield']) for m in months],
    }
    
    context = {
        'monthly_stats': monthly_stats,
        'chart_json': json.dumps(chart_data),
    }
    
    return render(request, 'forecast/historical_analysis.html', context)


@login_required(login_url='/login/')
def export_data(request, format='pdf'):
    """Export user's farming data to PDF or CSV"""
    from django.http import HttpResponse
    import csv
    from io import BytesIO
    
    user_farmers = Farmer.objects.filter(user=request.user).order_by('-created_at')
    
    if format == 'csv':
        # CSV Export
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="agri_forecast_data_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Mandal', 'Village', 'Crop', 'Acres', 'Sowing Date', 
                        'Disease', 'Severity', 'Predicted Yield', 'Current Price', 
                        'Peak Price', 'Recommendation'])
        
        for farmer in user_farmers:
            try:
                disease = DiseaseRecord.objects.filter(farmer=farmer).first()
                prediction = PredictionResult.objects.get(farmer=farmer)
                
                writer.writerow([
                    farmer.created_at.strftime('%Y-%m-%d'),
                    farmer.get_mandal_display(),
                    farmer.village,
                    farmer.get_crop_display(),
                    farmer.acres,
                    farmer.sowing_date,
                    disease.disease_name if disease else 'None',
                    disease.get_severity_display() if disease else '-',
                    f"{prediction.predicted_yield:.2f}",
                    f"₹{prediction.current_market_price:.2f}",
                    f"₹{prediction.predicted_peak_price:.2f}",
                    prediction.get_recommendation_display(),
                ])
            except PredictionResult.DoesNotExist:
                writer.writerow([
                    farmer.created_at.strftime('%Y-%m-%d'),
                    farmer.get_mandal_display(),
                    farmer.village,
                    farmer.get_crop_display(),
                    farmer.acres,
                    farmer.sowing_date,
                    '-', '-', '-', '-', '-', 'No Prediction'
                ])
        
        return response
    
    elif format == 'pdf':
        # Simple PDF Export (using HTML to PDF would need reportlab or weasyprint)
        # For now, return HTML that can be printed as PDF
        context = {
            'farmers': user_farmers,
            'export_date': timezone.now(),
        }
        response = render(request, 'forecast/export_pdf.html', context)
        response['Content-Disposition'] = f'attachment; filename="agri_forecast_report_{timezone.now().strftime("%Y%m%d")}.html"'
        return response
    
    else:
        messages.error(request, 'Invalid export format')
        return redirect('forecast:user_profile')


@login_required(login_url='/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def price_alerts(request):
    """Manage price alerts for crops - ADMIN ONLY"""
    from .models import PriceAlert
    
    if request.method == 'POST':
        crop = request.POST.get('crop')
        target_price = request.POST.get('target_price')
        
        if crop and target_price:
            try:
                target_price = float(target_price)
                PriceAlert.objects.create(
                    user=request.user,
                    crop=crop,
                    target_price=target_price
                )
                messages.success(request, f'Price alert set for {dict(CROP_CHOICES)[crop]} at ₹{target_price}/Q')
            except ValueError:
                messages.error(request, 'Invalid price value')
        else:
            messages.error(request, 'Please provide crop and target price')
        
        return redirect('forecast:price_alerts')
    
    # GET request - show alerts
    active_alerts = PriceAlert.objects.filter(
        user=request.user,
        is_active=True,
        is_triggered=False
    ).order_by('-created_at')
    
    triggered_alerts = PriceAlert.objects.filter(
        user=request.user,
        is_triggered=True
    ).order_by('-triggered_at')[:10]
    
    context = {
        'active_alerts': active_alerts,
        'triggered_alerts': triggered_alerts,
        'crop_choices': CROP_CHOICES,
    }
    
    return render(request, 'forecast/price_alerts.html', context)


@login_required(login_url='/login/')
def delete_alert(request, alert_id):
    """Delete a price alert"""
    from .models import PriceAlert
    
    try:
        alert = PriceAlert.objects.get(id=alert_id, user=request.user)
        alert.delete()
        messages.success(request, 'Price alert deleted successfully')
    except PriceAlert.DoesNotExist:
        messages.error(request, 'Alert not found')
    
    return redirect('forecast:price_alerts')


@login_required(login_url='/login/')
def toggle_favorite(request, crop):
    """Add or remove crop from favorites"""
    from .models import FavoriteCrop
    
    try:
        favorite = FavoriteCrop.objects.get(user=request.user, crop=crop)
        favorite.delete()
        messages.success(request, f'{dict(CROP_CHOICES)[crop]} removed from favorites')
    except FavoriteCrop.DoesNotExist:
        FavoriteCrop.objects.create(user=request.user, crop=crop)
        messages.success(request, f'{dict(CROP_CHOICES)[crop]} added to favorites')
    
    return redirect(request.META.get('HTTP_REFERER', 'forecast:user_profile'))


@login_required(login_url='/login/')
def notifications(request):
    """View and manage notifications"""
    from .models import Notification
    
    # Mark specific notification as read
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        if notification_id:
            try:
                notification = Notification.objects.get(id=notification_id, user=request.user)
                notification.is_read = True
                notification.read_at = timezone.now()
                notification.save()
            except Notification.DoesNotExist:
                pass
        return redirect('forecast:notifications')
    
    # GET - show all notifications
    all_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = all_notifications.filter(is_read=False).count()
    
    context = {
        'notifications': all_notifications,
        'unread_count': unread_count,
    }
    
    return render(request, 'forecast/notifications.html', context)


@login_required(login_url='/login/')
def mark_all_read(request):
    """Mark all notifications as read"""
    from .models import Notification
    
    Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )
    messages.success(request, 'All notifications marked as read')
    return redirect('forecast:notifications')


@login_required(login_url='/login/')
def crop_recommendations(request):
    """Get AI-powered crop recommendations based on user's history - Optimized version"""
    from django.db.models import Avg, Count, Sum
    from .models import Notification
    import json
    
    # Optimized query - analyze user's historical data
    user_crops = Farmer.objects.filter(user=request.user).values('crop').annotate(
        count=Count('id'),
        avg_profit=Avg('prediction__profit_delta'),
        total_yield=Sum('prediction__predicted_yield'),
        success_rate=Count('prediction__recommendation', filter=models.Q(prediction__recommendation='store'))
    ).order_by('-avg_profit')[:5]  # Limit to top 5
    
    # Get best performing crop
    best_crop = user_crops.first() if user_crops else None
    
    # Optimized mandal-wise performance query
    mandal_performance = Farmer.objects.filter(user=request.user).values('mandal').annotate(
        avg_yield=Avg('prediction__predicted_yield'),
        count=Count('id')
    ).order_by('-avg_yield')[:5]  # Limit to top 5
    
    # Generate recommendations
    recommendations = []
    
    if best_crop and best_crop['avg_profit']:
        crop_name = dict(CROP_CHOICES).get(best_crop['crop'], best_crop['crop'])
        recommendations.append({
            'title': f"Continue Growing {crop_name}",
            'reason': f"Your average profit: ₹{best_crop['avg_profit']:.2f} per submission",
            'confidence': 85,
        })
    
    # Season-based recommendations
    current_month = timezone.now().month
    if 6 <= current_month <= 9:  # Monsoon season
        recommendations.append({
            'title': 'Ideal for Paddy Cultivation',
            'reason': 'Monsoon season - High rainfall expected',
            'confidence': 90,
        })
    elif 10 <= current_month <= 2:  # Winter season
        recommendations.append({
            'title': 'Consider Chillies or Turmeric',
            'reason': 'Winter season - Good for spice crops',
            'confidence': 80,
        })
    else:  # Summer season (March-May)
        recommendations.append({
            'title': 'Summer Crops Recommended',
            'reason': 'Consider heat-tolerant crops like cotton or groundnut',
            'confidence': 75,
        })
    
    # Create notification for recommendations (only once per day)
    if recommendations and not Notification.objects.filter(
        user=request.user,
        notification_type='recommendation',
        created_at__date=timezone.now().date()
    ).exists():
        Notification.objects.create(
            user=request.user,
            notification_type='recommendation',
            title='New Crop Recommendations Available',
            message=f'We have {len(recommendations)} new recommendations based on your farming history'
        )
    
    context = {
        'recommendations': recommendations,
        'user_crops': user_crops,
        'mandal_performance': mandal_performance,
        'best_crop': best_crop,
    }
    
    return render(request, 'forecast/crop_recommendations.html', context)


# Admin Dashboard View
@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_dashboard(request):
    """Enhanced admin dashboard with comprehensive statistics and management links"""
    from django.db.models import Sum, Avg, Max, Min
    
    # Get statistics
    total_farmers = Farmer.objects.count()
    total_diseases = DiseaseRecord.objects.count()
    total_weather = WeatherData.objects.count()
    total_prices = MarketPrice.objects.count()
    total_users = User.objects.count()
    total_predictions = PredictionResult.objects.count()
    
    # User statistics
    total_admins = User.objects.filter(is_staff=True).count()
    total_regular_users = User.objects.filter(is_staff=False).count()
    active_users = User.objects.filter(is_active=True).count()
    
    # Recent farmers (last 10)
    recent_farmers = Farmer.objects.select_related('user').order_by('-created_at')[:10]
    
    # Recent predictions (last 10)
    recent_predictions = PredictionResult.objects.select_related('farmer').order_by('-generated_at')[:10]
    
    # Crop distribution
    crop_stats = Farmer.objects.values('crop').annotate(
        count=Count('id'),
        total_acres=Sum('acres')
    ).order_by('-count')
    
    # Mandal distribution
    mandal_stats = Farmer.objects.values('mandal').annotate(
        count=Count('id'),
        total_acres=Sum('acres')
    ).order_by('-count')
    
    # Disease severity distribution
    severity_stats = DiseaseRecord.objects.values('severity').annotate(
        count=Count('id')
    )
    
    # Recommendation distribution
    recommendation_stats = PredictionResult.objects.values('recommendation').annotate(
        count=Count('id')
    )
    
    # Monthly farmer registrations (last 6 months)
    from datetime import datetime, timedelta
    six_months_ago = datetime.now() - timedelta(days=180)
    monthly_farmers = Farmer.objects.filter(
        created_at__gte=six_months_ago
    ).values('created_at__month').annotate(count=Count('id'))
    
    # Average yield prediction
    avg_yield = PredictionResult.objects.aggregate(
        avg_predicted_yield=Avg('predicted_yield'),
        max_yield=Max('predicted_yield'),
        min_yield=Min('predicted_yield')
    )
    
    # Storage & cash statistics
    farmers_with_storage = Farmer.objects.filter(cold_storage=True).count()
    farmers_urgent_cash = Farmer.objects.filter(urgent_cash=True).count()
    
    context = {
        # Basic counts
        'total_farmers': total_farmers,
        'total_diseases': total_diseases,
        'total_weather': total_weather,
        'total_prices': total_prices,
        'total_users': total_users,
        'total_predictions': total_predictions,
        
        # User stats
        'total_admins': total_admins,
        'total_regular_users': total_regular_users,
        'active_users': active_users,
        
        # Recent data
        'recent_farmers': recent_farmers,
        'recent_predictions': recent_predictions,
        
        # Distribution stats
        'crop_stats': crop_stats,
        'mandal_stats': mandal_stats,
        'severity_stats': severity_stats,
        'recommendation_stats': recommendation_stats,
        
        # Additional stats
        'avg_yield': avg_yield,
        'farmers_with_storage': farmers_with_storage,
        'farmers_urgent_cash': farmers_urgent_cash,
        'percentage_storage': round((farmers_with_storage / total_farmers * 100), 1) if total_farmers > 0 else 0,
        'percentage_urgent_cash': round((farmers_urgent_cash / total_farmers * 100), 1) if total_farmers > 0 else 0,
    }
    
    return render(request, 'forecast/admin_dashboard.html', context)


# User Login View
def user_login(request):
    if request.user.is_authenticated:
        return redirect('forecast:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('forecast:home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'forecast/user_login.html')


# User Register View
def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'forecast/user_register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return render(request, 'forecast/user_register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return render(request, 'forecast/user_register.html')
        
        # Create regular user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('forecast:user_login')
    
    return render(request, 'forecast/user_register.html')


# Logout View
def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('forecast:home')


# User Profile View
@login_required(login_url='/login/')
def user_profile(request):
    """Enhanced user dashboard with comprehensive statistics"""
    from django.db.models import Count, Avg, Sum, Q
    from .models import PriceAlert, FavoriteCrop, Notification
    import json
    from datetime import timedelta
    
    # Get farmer submissions for current user
    user_farmers = Farmer.objects.filter(
        user=request.user
    ).order_by('-created_at')[:20]
    
    # Get predictions for user's farmers
    user_predictions = PredictionResult.objects.filter(
        farmer__user=request.user
    ).order_by('-generated_at')[:10]
    
    # Calculate statistics
    total_submissions = Farmer.objects.filter(user=request.user).count()
    total_predictions = PredictionResult.objects.filter(farmer__user=request.user).count()
    
    # Crop wise statistics
    crop_stats = Farmer.objects.filter(user=request.user).values('crop').annotate(
        count=Count('id'),
        avg_acres=Avg('acres')
    ).order_by('-count')
    
    # Recent disease records
    recent_diseases = DiseaseRecord.objects.filter(
        farmer__user=request.user
    ).order_by('-detection_date')[:5]
    
    # Yield statistics
    yield_stats = PredictionResult.objects.filter(
        farmer__user=request.user
    ).aggregate(
        avg_yield=Avg('predicted_yield'),
        total_yield=Sum('predicted_yield'),
        avg_current_value=Avg('total_current_value'),
        total_current_value=Sum('total_current_value'),
        total_future_value=Sum('total_future_value'),
        total_profit_delta=Sum('profit_delta')
    )
    
    # Get active price alerts
    active_alerts = PriceAlert.objects.filter(
        user=request.user,
        is_active=True,
        is_triggered=False
    ).order_by('-created_at')[:5]
    
    # Get favorite crops
    favorite_crops = FavoriteCrop.objects.filter(user=request.user)
    
    # Get unread notifications
    unread_notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    # Chart data for crop distribution (JSON)
    crop_chart_data = {
        'labels': [item['crop'] for item in crop_stats],
        'data': [item['count'] for item in crop_stats]
    }
    
    context = {
        'user_farmers': user_farmers,
        'user_predictions': user_predictions,
        'total_submissions': total_submissions,
        'total_predictions': total_predictions,
        'crop_stats': crop_stats,
        'recent_diseases': recent_diseases,
        'yield_stats': yield_stats,
        'active_alerts': active_alerts,
        'favorite_crops': favorite_crops,
        'unread_notifications': unread_notifications,
        'crop_chart_json': json.dumps(crop_chart_data),
    }
    
    return render(request, 'forecast/user_profile.html', context)


@login_required(login_url='/login/')
def farmer_detail(request, farmer_id):
    """
    View detailed information about a specific farmer submission
    """
    try:
        farmer = Farmer.objects.get(id=farmer_id)
        disease_record = DiseaseRecord.objects.filter(farmer=farmer).first()
        
        # Get price prediction for the farmer's crop
        price_prediction = predict_market_price(farmer.crop)
        
        # Get weather data for farmer's mandal
        weather_data = WeatherData.objects.filter(mandal=farmer.mandal).order_by('-date').first()
        
        # Get market prices for farmer's crop
        market_prices = MarketPrice.objects.filter(crop=farmer.crop).order_by('-date')[:5]
        
        # Calculate yield prediction
        rainfall = weather_data.rainfall if weather_data else 75.0
        temperature = weather_data.temperature if weather_data else 28.0
        humidity = weather_data.humidity if weather_data else 70.0
        disease_severity = disease_record.severity if disease_record else 'low'
        
        yield_prediction = predict_crop_yield(
            crop_type=farmer.crop,
            acres=farmer.acres,
            rainfall=rainfall,
            temperature=temperature,
            humidity=humidity,
            disease_severity=disease_severity
        )
        
        # Calculate selling recommendation
        selling_recommendation = None
        if not price_prediction.get('error') and yield_prediction:
            selling_recommendation = calculate_selling_recommendation(
                predicted_yield=yield_prediction['predicted_yield'],
                current_price=price_prediction['current_price'],
                peak_price=price_prediction['predicted_peak_price'],
                cold_storage_available=farmer.cold_storage,
                urgent_cash_needed=farmer.urgent_cash
            )
        
        context = {
            'page': 'farmer_detail',
            'farmer': farmer,
            'disease_record': disease_record,
            'price_prediction': price_prediction,
            'weather_data': weather_data,
            'market_prices': market_prices,
            'yield_prediction': yield_prediction,
            'selling_recommendation': selling_recommendation,
        }
        
        return render(request, 'forecast/farmer_detail.html', context)
        
    except Farmer.DoesNotExist:
        messages.error(request, 'Farmer record not found.')
        return redirect('forecast:home')


# Data Analytics View
@user_passes_test(lambda u: u.is_staff)
def data_analytics(request):
    """
    Comprehensive view showing all weather data and market prices
    organized by mandal and crop
    """
    from django.db.models import Min, Max
    from collections import defaultdict
    
    # Weather Data Statistics
    total_weather = WeatherData.objects.count()
    weather_mandals = WeatherData.objects.values_list('mandal', flat=True).distinct()
    weather_date_range = WeatherData.objects.aggregate(
        min_date=Min('date'),
        max_date=Max('date')
    )
    
    # Group weather data by mandal
    weather_by_mandal = defaultdict(list)
    for weather in WeatherData.objects.all().order_by('mandal', '-date'):
        weather_by_mandal[weather.mandal].append(weather)
    
    # Market Price Statistics
    total_prices = MarketPrice.objects.count()
    price_crops = MarketPrice.objects.values_list('crop', flat=True).distinct()
    price_date_range = MarketPrice.objects.aggregate(
        min_date=Min('date'),
        max_date=Max('date')
    )
    
    # Group prices by crop with display names
    prices_by_crop = []
    for crop_key in price_crops:
        crop_obj = MarketPrice.objects.filter(crop=crop_key).first()
        if crop_obj:
            crop_name = crop_obj.get_crop_display()
            crop_prices = MarketPrice.objects.filter(crop=crop_key).order_by('-date')
            prices_by_crop.append((crop_key, crop_name, crop_prices))
    
    context = {
        'total_weather': total_weather,
        'weather_mandals': weather_mandals,
        'weather_date_range': (weather_date_range['min_date'], weather_date_range['max_date']),
        'weather_by_mandal': dict(weather_by_mandal),
        'total_prices': total_prices,
        'price_crops': price_crops,
        'price_date_range': (price_date_range['min_date'], price_date_range['max_date']),
        'prices_by_crop': prices_by_crop,
    }
    
    return render(request, 'forecast/data_analytics.html', context)


# ========================================
# Enhanced Admin Management Views
# ========================================

# Admin User Management
@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_users(request):
    """Manage all users - view, search, filter"""
    users = User.objects.all().order_by('-date_joined')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            username__icontains=search_query
        ) | users.filter(
            email__icontains=search_query
        )
    
    # Filter by staff status
    filter_staff = request.GET.get('staff', '')
    if filter_staff == 'true':
        users = users.filter(is_staff=True)
    elif filter_staff == 'false':
        users = users.filter(is_staff=False)
    
    context = {
        'users': users,
        'search_query': search_query,
        'total_users': User.objects.count(),
        'total_admins': User.objects.filter(is_staff=True).count(),
        'total_regular': User.objects.filter(is_staff=False).count(),
    }
    
    return render(request, 'forecast/admin_users.html', context)


@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_user_create(request):
    """Create new user"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        is_staff = request.POST.get('is_staff') == 'on'
        is_superuser = request.POST.get('is_superuser') == 'on'
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('forecast:admin_user_create')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.save()
        
        messages.success(request, f'User {username} created successfully!')
        return redirect('forecast:admin_users')
    
    return render(request, 'forecast/admin_user_create.html')


@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_user_edit(request, user_id):
    """Edit existing user"""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found!')
        return redirect('forecast:admin_users')
    
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_superuser = request.POST.get('is_superuser') == 'on'
        user.is_active = request.POST.get('is_active') == 'on'
        
        # Update password if provided
        new_password = request.POST.get('password')
        if new_password:
            user.set_password(new_password)
        
        user.save()
        messages.success(request, f'User {user.username} updated successfully!')
        return redirect('forecast:admin_users')
    
    context = {'edit_user': user}
    return render(request, 'forecast/admin_user_edit.html', context)


@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_user_delete(request, user_id):
    """Delete user"""
    try:
        user = User.objects.get(id=user_id)
        
        # Prevent deleting yourself
        if user.id == request.user.id:
            messages.error(request, 'You cannot delete your own account!')
            return redirect('forecast:admin_users')
        
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully!')
    except User.DoesNotExist:
        messages.error(request, 'User not found!')
    
    return redirect('forecast:admin_users')


# Admin Farmer Management
@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_farmers(request):
    """Manage all farmer records"""
    farmers = Farmer.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        farmers = farmers.filter(
            village__icontains=search_query
        ) | farmers.filter(
            crop__icontains=search_query
        )
    
    # Filter by mandal
    mandal_filter = request.GET.get('mandal', '')
    if mandal_filter:
        farmers = farmers.filter(mandal=mandal_filter)
    
    # Filter by crop
    crop_filter = request.GET.get('crop', '')
    if crop_filter:
        farmers = farmers.filter(crop=crop_filter)
    
    context = {
        'farmers': farmers,
        'search_query': search_query,
        'total_farmers': Farmer.objects.count(),
        'mandals': ['machilipatnam', 'gudivada', 'vuyyur'],
        'crops': ['paddy', 'mango', 'chillies', 'cotton', 'turmeric', 'sugarcane', 'banana'],
    }
    
    return render(request, 'forecast/admin_farmers.html', context)


@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_farmer_detail(request, farmer_id):
    """View detailed information about a specific farmer (Admin view)"""
    try:
        farmer = Farmer.objects.get(id=farmer_id)
    except Farmer.DoesNotExist:
        messages.error(request, 'Farmer record not found!')
        return redirect('forecast:admin_farmers')
    
    # Get related data
    disease_record = DiseaseRecord.objects.filter(farmer=farmer).first()
    prediction_result = PredictionResult.objects.filter(farmer=farmer).first()
    
    # Get weather data for farmer's mandal
    weather_data = WeatherData.objects.filter(mandal=farmer.mandal).order_by('-date').first()
    
    # Get market prices for farmer's crop
    market_prices = MarketPrice.objects.filter(crop=farmer.crop).order_by('-date')[:5]
    
    context = {
        'farmer': farmer,
        'disease_record': disease_record,
        'prediction_result': prediction_result,
        'weather_data': weather_data,
        'market_prices': market_prices,
    }
    
    return render(request, 'forecast/farmer_detail.html', context)


@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_farmer_edit(request, farmer_id):
    """Edit farmer record"""
    try:
        farmer = Farmer.objects.get(id=farmer_id)
    except Farmer.DoesNotExist:
        messages.error(request, 'Farmer record not found!')
        return redirect('forecast:admin_farmers')
    
    if request.method == 'POST':
        farmer.village = request.POST.get('village')
        farmer.mandal = request.POST.get('mandal')
        farmer.crop = request.POST.get('crop')
        farmer.acres = float(request.POST.get('acres'))
        farmer.sowing_date = request.POST.get('sowing_date')
        farmer.cold_storage = request.POST.get('cold_storage') == 'on'
        farmer.urgent_cash = request.POST.get('urgent_cash') == 'on'
        farmer.save()
        
        messages.success(request, 'Farmer record updated successfully!')
        return redirect('forecast:admin_farmers')
    
    context = {'farmer': farmer}
    return render(request, 'forecast/admin_farmer_edit.html', context)


@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_farmer_delete(request, farmer_id):
    """Delete farmer record"""
    try:
        farmer = Farmer.objects.get(id=farmer_id)
        village = farmer.village
        farmer.delete()
        messages.success(request, f'Farmer record from {village} deleted successfully!')
    except Farmer.DoesNotExist:
        messages.error(request, 'Farmer record not found!')
    
    return redirect('forecast:admin_farmers')


@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_farmers_bulk_delete(request):
    """Bulk delete farmer records"""
    if request.method == 'POST':
        farmer_ids = request.POST.getlist('farmer_ids')
        if farmer_ids:
            Farmer.objects.filter(id__in=farmer_ids).delete()
            messages.success(request, f'{len(farmer_ids)} farmer records deleted successfully!')
        else:
            messages.warning(request, 'No farmers selected for deletion!')
    
    return redirect('forecast:admin_farmers')


# Admin Weather Data Management
@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_weather(request):
    """Manage weather data"""
    weather_data = WeatherData.objects.all().order_by('-date')[:100]  # Latest 100 records
    
    # Filter by mandal
    mandal_filter = request.GET.get('mandal', '')
    if mandal_filter:
        weather_data = WeatherData.objects.filter(mandal=mandal_filter).order_by('-date')[:100]
    
    context = {
        'weather_data': weather_data,
        'total_weather': WeatherData.objects.count(),
        'mandals': ['machilipatnam', 'gudivada', 'vuyyur'],
    }
    
    return render(request, 'forecast/admin_weather.html', context)


@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_weather_add(request):
    """Add new weather data"""
    if request.method == 'POST':
        mandal = request.POST.get('mandal')
        rainfall = float(request.POST.get('rainfall'))
        temperature = float(request.POST.get('temperature'))
        humidity = float(request.POST.get('humidity'))
        date_str = request.POST.get('date')
        
        WeatherData.objects.create(
            mandal=mandal,
            rainfall=rainfall,
            temperature=temperature,
            humidity=humidity,
            date=date_str
        )
        
        messages.success(request, 'Weather data added successfully!')
        return redirect('forecast:admin_weather')
    
    context = {
        'mandals': ['machilipatnam', 'gudivada', 'vuyyur'],
    }
    return render(request, 'forecast/admin_weather_add.html', context)


@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_weather_delete(request, weather_id):
    """Delete weather record"""
    try:
        weather = WeatherData.objects.get(id=weather_id)
        weather.delete()
        messages.success(request, 'Weather record deleted successfully!')
    except WeatherData.DoesNotExist:
        messages.error(request, 'Weather record not found!')
    
    return redirect('forecast:admin_weather')


# Admin Market Price Management
@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_prices(request):
    """Manage market prices"""
    prices = MarketPrice.objects.all().order_by('-date')[:100]  # Latest 100 records
    
    # Filter by crop
    crop_filter = request.GET.get('crop', '')
    if crop_filter:
        prices = MarketPrice.objects.filter(crop=crop_filter).order_by('-date')[:100]
    
    context = {
        'prices': prices,
        'total_prices': MarketPrice.objects.count(),
        'crops': ['paddy', 'mango', 'chillies', 'cotton', 'turmeric', 'sugarcane', 'banana'],
    }
    
    return render(request, 'forecast/admin_prices.html', context)


@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_price_add(request):
    """Add new market price"""
    if request.method == 'POST':
        crop = request.POST.get('crop')
        region = request.POST.get('region')
        price_per_quintal = float(request.POST.get('price_per_quintal'))
        date_str = request.POST.get('date')
        is_peak_season = request.POST.get('is_peak_season') == 'on'
        
        MarketPrice.objects.create(
            crop=crop,
            region=region,
            price_per_quintal=price_per_quintal,
            date=date_str,
            is_peak_season=is_peak_season
        )
        
        messages.success(request, 'Market price added successfully!')
        return redirect('forecast:admin_prices')
    
    context = {
        'crops': ['paddy', 'mango', 'chillies', 'cotton', 'turmeric', 'sugarcane', 'banana'],
    }
    return render(request, 'forecast/admin_price_add.html', context)


@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_price_delete(request, price_id):
    """Delete market price record"""
    try:
        price = MarketPrice.objects.get(id=price_id)
        price.delete()
        messages.success(request, 'Market price record deleted successfully!')
    except MarketPrice.DoesNotExist:
        messages.error(request, 'Market price record not found!')
    
    return redirect('forecast:admin_prices')


# Export Functions
@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_export_farmers(request):
    """Export farmer data to CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="farmers_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Village', 'Mandal', 'Crop', 'Acres', 'Sowing Date', 
                     'Cold Storage', 'Urgent Cash', 'Created At'])
    
    farmers = Farmer.objects.all()
    for farmer in farmers:
        writer.writerow([
            farmer.id,
            farmer.village,
            farmer.get_mandal_display(),
            farmer.get_crop_display(),
            farmer.acres,
            farmer.sowing_date,
            'Yes' if farmer.cold_storage else 'No',
            'Yes' if farmer.urgent_cash else 'No',
            farmer.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response


@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_export_weather(request):
    """Export weather data to CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="weather_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Mandal', 'Rainfall (mm)', 'Temperature (°C)', 
                     'Humidity (%)', 'Date'])
    
    weather_data = WeatherData.objects.all()
    for weather in weather_data:
        writer.writerow([
            weather.id,
            weather.get_mandal_display(),
            weather.rainfall,
            weather.temperature,
            weather.humidity,
            weather.date
        ])
    
    return response


@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_export_prices(request):
    """Export market prices to CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="prices_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Crop', 'Region', 'Price per Quintal (₹)', 
                     'Peak Season', 'Date'])
    
    prices = MarketPrice.objects.all()
    for price in prices:
        writer.writerow([
            price.id,
            price.get_crop_display(),
            price.region,
            price.price_per_quintal,
            'Yes' if price.is_peak_season else 'No',
            price.date
        ])
    
    return response


# Admin Logs Viewer
@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_logs(request):
    """View application logs"""
    import os
    from pathlib import Path
    
    log_file = Path(__file__).resolve().parent.parent / 'logs' / 'django.log'
    logs = []
    
    if log_file.exists():
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                # Get last 200 lines
                logs = lines[-200:]
                logs.reverse()
                # Strip whitespace from each line
                logs = [line.strip() for line in logs if line.strip()]
        except Exception as e:
            messages.error(request, f'Error reading log file: {str(e)}')
    else:
        messages.info(request, 'No log file found yet.')
    
    context = {
        'logs': logs,
        'log_file_path': str(log_file),
    }
    
    return render(request, 'forecast/admin_logs.html', context)


# Admin Settings
@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_settings(request):
    """Admin settings and configuration"""
    from django.conf import settings
    import sys
    import django
    
    if request.method == 'POST':
        # Handle settings update
        messages.info(request, 'Settings update feature coming soon!')
    
    context = {
        'debug_mode': settings.DEBUG,
        'time_zone': settings.TIME_ZONE,
        'language_code': settings.LANGUAGE_CODE,
        'total_users': User.objects.count(),
        'total_farmers': Farmer.objects.count(),
        'total_predictions': PredictionResult.objects.count(),
        'total_weather': WeatherData.objects.count(),
        'total_prices': MarketPrice.objects.count(),
        'total_diseases': DiseaseRecord.objects.count(),
        'django_version': django.get_version(),
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'db_engine': settings.DATABASES['default']['ENGINE'].split('.')[-1].upper(),
        'db_name': settings.DATABASES['default']['NAME'],
        'media_root': settings.MEDIA_URL,
        'static_root': settings.STATIC_URL,
    }
    
    return render(request, 'forecast/admin_settings.html', context)


@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_create_notification(request):
    """Create and send notifications to users"""
    from .models import Notification
    
    if request.method == 'POST':
        notification_type = request.POST.get('notification_type')
        title = request.POST.get('title')
        message = request.POST.get('message')
        send_to = request.POST.get('send_to')  # 'all', 'active', 'staff', 'specific'
        specific_user_ids = request.POST.getlist('user_ids')
        
        if title and message and notification_type:
            # Determine recipients
            if send_to == 'all':
                users = User.objects.all()
            elif send_to == 'active':
                users = User.objects.filter(is_active=True)
            elif send_to == 'staff':
                users = User.objects.filter(is_staff=True)
            elif send_to == 'specific' and specific_user_ids:
                users = User.objects.filter(id__in=specific_user_ids)
            else:
                users = User.objects.none()
            
            # Create notifications for selected users
            notifications_created = 0
            for user in users:
                Notification.objects.create(
                    user=user,
                    notification_type=notification_type,
                    title=title,
                    message=message
                )
                notifications_created += 1
            
            messages.success(request, f'Successfully created {notifications_created} notification(s)!')
            return redirect('forecast:admin_dashboard')
        else:
            messages.error(request, 'Please fill in all required fields')
    
    # GET request - show form
    all_users = User.objects.all().order_by('username')
    
    context = {
        'all_users': all_users,
        'notification_types': [
            ('price_alert', 'Price Alert'),
            ('recommendation', 'Recommendation'),
            ('weather_update', 'Weather Update'),
            ('system', 'System Notification')
        ]
    }
    
    return render(request, 'forecast/admin_create_notification.html', context)
