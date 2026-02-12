"""
Views for the forecast app
Handles all the logic for crop forecasting system
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from .models import Farmer, DiseaseRecord, WeatherData, MarketPrice, PredictionResult
from datetime import datetime, timedelta
from django.db.models import Count, Avg
import json
import random


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
            # Return default values if no price data found
            return {
                'current_price': 0,
                'predicted_peak_price': 0,
                'increase_percentage': 0,
                'best_selling_start': None,
                'best_selling_end': None,
                'recommendation': 'No market price data available for this crop.',
                'price_date': None,
                'error': True
            }
        
        current_price = latest_price.price_per_quintal
        price_date = latest_price.date
        
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
    
    # Step 4: Return complete prediction
    return {
        'current_price': round(current_price, 2),
        'predicted_peak_price': predicted_peak_price,
        'increase_percentage': increase_percentage,
        'best_selling_start': best_selling_start.strftime('%Y-%m-%d'),
        'best_selling_end': best_selling_end.strftime('%Y-%m-%d'),
        'recommendation': recommendation,
        'price_date': price_date.strftime('%Y-%m-%d'),
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
    """
    farmer_id = request.session.get('farmer_id')
    
    if not farmer_id:
        messages.warning(request, 'Please submit farmer data first.')
        return redirect('forecast:farmer_input')
    
    try:
        farmer = Farmer.objects.get(id=farmer_id)
        disease_record = DiseaseRecord.objects.filter(farmer=farmer).first()
        
        # Get price prediction for the farmer's crop
        price_prediction = predict_market_price(farmer.crop)
        
        # Get weather data for yield prediction
        weather_data = WeatherData.objects.filter(mandal=farmer.mandal).order_by('-date').first()
        
        # Set default weather values if no data available
        rainfall = weather_data.rainfall if weather_data else 75.0
        temperature = weather_data.temperature if weather_data else 28.0
        humidity = weather_data.humidity if weather_data else 70.0
        
        # Get disease severity
        disease_severity = disease_record.severity if disease_record else 'low'
        
        # Calculate yield prediction
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
        
        # Save PredictionResult to database
        if yield_prediction and not price_prediction.get('error') and selling_recommendation:
            # Parse peak price date
            peak_date = None
            if price_prediction.get('best_selling_start'):
                try:
                    peak_date = datetime.strptime(price_prediction['best_selling_start'], '%Y-%m-%d').date()
                except:
                    peak_date = None
            
            # Calculate yield reduction percentage
            yield_reduction = 0
            if yield_prediction.get('base_yield', 0) > 0:
                yield_reduction = ((yield_prediction['base_yield'] - yield_prediction['predicted_yield']) / yield_prediction['base_yield']) * 100
            
            # Calculate confidence score based on available data
            confidence = 70.0  # Base confidence
            if weather_data:
                confidence += 15.0  # Boost if real weather data available
            if disease_record:
                confidence += 15.0  # Boost if disease data available
            
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
                    'confidence_score': confidence,
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
                
                # Get disease severity from form (optional)
                severity = request.POST.get('severity', 'low').lower()
                if severity not in ['low', 'medium', 'high']:
                    severity = 'low'
                
                # Calculate yield loss based on severity
                yield_loss = calculate_yield_loss(severity)
                
                # Create disease record with image
                DiseaseRecord.objects.create(
                    farmer=farmer,
                    image=crop_image,
                    severity=severity,
                    yield_loss_percentage=yield_loss,
                    detection_date=datetime.now().date(),
                    disease_name=request.POST.get('disease_name', 'Pending AI Analysis')
                )
            
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
        if admin_secret != 'AGRI2026':
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


# Admin Dashboard View
@user_passes_test(is_admin, login_url='/af-admin/login/')
def admin_dashboard(request):
    # Get statistics
    total_farmers = Farmer.objects.count()
    total_diseases = DiseaseRecord.objects.count()
    total_weather = WeatherData.objects.count()
    total_prices = MarketPrice.objects.count()
    
    # Recent farmers
    recent_farmers = Farmer.objects.order_by('-id')[:10]
    
    # Crop distribution
    crop_stats = Farmer.objects.values('crop').annotate(count=Count('id'))
    
    # Mandal distribution
    mandal_stats = Farmer.objects.values('mandal').annotate(count=Count('id'))
    
    context = {
        'total_farmers': total_farmers,
        'total_diseases': total_diseases,
        'total_weather': total_weather,
        'total_prices': total_prices,
        'recent_farmers': recent_farmers,
        'crop_stats': crop_stats,
        'mandal_stats': mandal_stats,
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
    # Get all farmer submissions (since Farmer model doesn't track user relationship)
    user_farmers = Farmer.objects.all().order_by('-id')[:10]
    
    context = {
        'user_farmers': user_farmers,
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


# ==============================================================================
# Custom Error Handlers for Production
# ==============================================================================

def custom_404(request, exception):
    """Custom 404 error handler"""
    return render(request, '404.html', status=404)


def custom_500(request):
    """Custom 500 error handler"""
    return render(request, '500.html', status=500)


def custom_403(request, exception):
    """Custom 403 error handler"""
    return render(request, '403.html', status=403)


def custom_400(request, exception):
    """Custom 400 error handler"""
    return render(request, '400.html', status=400)
