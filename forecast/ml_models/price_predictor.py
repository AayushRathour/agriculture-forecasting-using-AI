"""
Price Prediction Model
Uses machine learning and time series analysis to predict crop prices
Considers historical prices, seasonal trends, and market conditions
"""

import os
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib


class PricePredictor:
    """
    Market Price Prediction using Machine Learning
    
    Predicts future crop prices based on:
    - Historical price data
    - Seasonal trends
    - Supply-demand dynamics
    - Market conditions
    """
    
    def __init__(self, model_path=None):
        """
        Initialize the price predictor
        
        Args:
            model_path (str): Path to pre-trained model file
        """
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), 
            'trained_models', 
            'price_model.pkl'
        )
        self.scaler_path = os.path.join(
            os.path.dirname(__file__), 
            'trained_models', 
            'price_scaler.pkl'
        )
        
        # Historical baseline prices for Krishna District (₹/quintal)
        self.baseline_prices = {
            'paddy': {
                'average': 2200,
                'min': 1800,
                'max': 2800,
                'peak_months': [11, 12, 1],  # November, December, January
                'low_months': [5, 6, 7]      # May, June, July (harvest season)
            },
            'mango': {
                'average': 3200,
                'min': 2000,
                'max': 5000,
                'peak_months': [3, 4],       # March, April (pre-harvest)
                'low_months': [5, 6]         # May, June (peak harvest)
            },
            'chillies': {
                'average': 9000,
                'min': 6000,
                'max': 15000,
                'peak_months': [1, 12],      # December, January
                'low_months': [3, 4]         # March, April (harvest)
            },
            'cotton': {
                'average': 7200,
                'min': 5500,
                'max': 9500,
                'peak_months': [9, 10],      # September, October
                'low_months': [12, 1, 2]     # December-February (harvest)
            },
            'turmeric': {
                'average': 9500,
                'min': 7000,
                'max': 13000,
                'peak_months': [12, 1],      # December, January
                'low_months': [3, 4]         # March, April (harvest)
            },
            'sugarcane': {
                'average': 350,
                'min': 280,
                'max': 450,
                'peak_months': [11, 12],     # November, December
                'low_months': [2, 3]         # February, March (harvest)
            },
            'banana': {
                'average': 1800,
                'min': 1200,
                'max': 2800,
                'peak_months': [11, 12, 1, 2],  # Winter months
                'low_months': [5, 6, 7]      # Summer months
            },
            'tomato': {
                'average': 1400,
                'min': 600,
                'max': 3500,
                'peak_months': [4, 5, 6],    # April-June (less supply)
                'low_months': [11, 12, 1]    # November-January (peak harvest)
            },
            'okra': {
                'average': 2200,
                'min': 1200,
                'max': 4000,
                'peak_months': [3, 4, 11],   # March, April, November
                'low_months': [1, 2, 6, 7]   # Peak harvest periods
            },
            'brinjal': {
                'average': 2000,
                'min': 1000,
                'max': 3500,
                'peak_months': [4, 5],       # April, May
                'low_months': [12, 1]        # December, January (harvest)
            },
            'maize': {
                'average': 2100,
                'min': 1700,
                'max': 2800,
                'peak_months': [1, 8],       # January, August
                'low_months': [3, 4, 10, 11] # Harvest periods
            },
            'groundnut': {
                'average': 6200,
                'min': 4800,
                'max': 8500,
                'peak_months': [7, 8],       # July, August
                'low_months': [10, 11]       # October, November (harvest)
            }
        }
        
        # Load model if exists
        self.model = None
        self.scaler = None
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model if available"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                print(f"Price prediction model loaded from {self.model_path}")
            
            if os.path.exists(self.scaler_path):
                self.scaler = joblib.load(self.scaler_path)
                print(f"Scaler loaded from {self.scaler_path}")
        except Exception as e:
            print(f"Could not load pre-trained model: {e}")
            self.model = None
            self.scaler = None
    
    def _encode_crop(self, crop_type):
        """Encode crop type as numerical value"""
        crop_codes = {
            'paddy': 1, 'mango': 2, 'chillies': 3, 'cotton': 4,
            'turmeric': 5, 'sugarcane': 6, 'banana': 7, 'tomato': 8,
            'okra': 9, 'brinjal': 10, 'maize': 11, 'groundnut': 12
        }
        return crop_codes.get(crop_type.lower(), 0)
    
    def calculate_seasonal_factor(self, crop_type, month):
        """
        Calculate seasonal price adjustment factor
        
        Args:
            crop_type (str): Crop name
            month (int): Month (1-12)
        
        Returns:
            float: Seasonal multiplier (0.7 to 1.3)
        """
        crop_data = self.baseline_prices.get(crop_type.lower())
        if not crop_data:
            return 1.0
        
        peak_months = crop_data.get('peak_months', [])
        low_months = crop_data.get('low_months', [])
        
        if month in peak_months:
            # Peak season - higher prices (10-30% above average)
            return np.random.uniform(1.1, 1.3)
        elif month in low_months:
            # Low season - lower prices (20-30% below average)
            return np.random.uniform(0.7, 0.85)
        else:
            # Normal season
            return np.random.uniform(0.95, 1.05)
    
    def predict(self, crop_type, current_price=None, region='Vijayawada',
                supply_level='normal', demand_level='normal'):
        """
        Predict future crop prices
        
        Args:
            crop_type (str): Type of crop
            current_price (float): Current market price (optional)
            region (str): Market region
            supply_level (str): Supply level (low/normal/high)
            demand_level (str): Demand level (low/normal/high)
        
        Returns:
            dict: Price prediction results
                - current_price: Current/baseline price
                - predicted_peak_price: Expected peak price
                - predicted_low_price: Expected lowest price
                - price_increase_percent: Expected price increase
                - best_selling_period: Recommended selling timeframe
                - confidence: Prediction confidence (0-100)
                - explanation: Detailed breakdown
        """
        
        # Get crop baseline data
        crop_data = self.baseline_prices.get(
            crop_type.lower(),
            {'average': 2500, 'min': 2000, 'max': 3500,
             'peak_months': [1], 'low_months': [6]}
        )
        
        # Use current price or baseline average
        if current_price is None or current_price <= 0:
            current_price = crop_data['average']
        
        current_date = datetime.now()
        current_month = current_date.month
        
        # Calculate seasonal factor for current month
        current_seasonal_factor = self.calculate_seasonal_factor(
            crop_type, current_month
        )
        
        # Try ML prediction first
        if self.model is not None:
            try:
                prediction_result = self._ml_prediction(
                    crop_type, current_price, current_month,
                    supply_level, demand_level, crop_data
                )
                prediction_result['method'] = 'machine_learning'
                return prediction_result
            except Exception as e:
                print(f"ML prediction failed: {e}")
                # Fall through to statistical prediction
        
        # Statistical prediction (fallback)
        return self._statistical_prediction(
            crop_type, current_price, current_month,
            supply_level, demand_level, crop_data
        )
    
    def _ml_prediction(self, crop_type, current_price, current_month,
                       supply_level, demand_level, crop_data):
        """ML-based price prediction"""
        
        # Prepare features
        crop_code = self._encode_crop(crop_type)
        
        supply_codes = {'low': 0, 'normal': 1, 'high': 2}
        demand_codes = {'low': 0, 'normal': 1, 'high': 2}
        
        supply_code = supply_codes.get(supply_level.lower(), 1)
        demand_code = demand_codes.get(demand_level.lower(), 1)
        
        features = np.array([
            crop_code,
            current_price,
            current_month,
            supply_code,
            demand_code
        ]).reshape(1, -1)
        
        # Scale if scaler available
        if self.scaler is not None:
            features = self.scaler.transform(features)
        
        # Predict peak price
        predicted_peak_price = self.model.predict(features)[0]
        
        # Calculate other metrics
        price_increase = predicted_peak_price - current_price
        price_increase_percent = (price_increase / current_price) * 100 if current_price > 0 else 0
        
        # Find best selling period (peak months)
        peak_months = crop_data.get('peak_months', [current_month])
        
        # Calculate dates
        best_selling_dates = self._calculate_selling_window(current_month, peak_months)
        
        return {
            'current_price': round(current_price, 2),
            'predicted_peak_price': round(predicted_peak_price, 2),
            'predicted_low_price': round(current_price * 0.85, 2),
            'price_increase': round(price_increase, 2),
            'price_increase_percent': round(price_increase_percent, 2),
            'best_selling_start': best_selling_dates['start'],
            'best_selling_end': best_selling_dates['end'],
            'confidence': 85.0,
            'explanation': f'ML model predicts peak price of ₹{predicted_peak_price:.2f}/quintal ({price_increase_percent:.1f}% increase)',
            'peak_months': peak_months
        }
    
    def _statistical_prediction(self, crop_type, current_price, current_month,
                                supply_level, demand_level, crop_data):
        """Statistical/rule-based price prediction"""
        
        # Base prediction on historical data
        average_price = crop_data['average']
        max_price = crop_data['max']
        min_price = crop_data['min']
        peak_months = crop_data['peak_months']
        
        # Adjust based on supply and demand
        supply_multiplier = {'low': 1.2, 'normal': 1.0, 'high': 0.85}
        demand_multiplier = {'low': 0.9, 'normal': 1.0, 'high': 1.15}
        
        supply_factor = supply_multiplier.get(supply_level.lower(), 1.0)
        demand_factor = demand_multiplier.get(demand_level.lower(), 1.0)
        
        # Calculate peak price
        # Use current price as baseline, adjust for peak season
        peak_seasonal_factor = 1.0
        for month in peak_months:
            factor = self.calculate_seasonal_factor(crop_type, month)
            peak_seasonal_factor = max(peak_seasonal_factor, factor)
        
        # Combine all factors
        combined_factor = peak_seasonal_factor * supply_factor * demand_factor
        combined_factor = min(combined_factor, 1.5)  # Cap at 50% increase
        
        predicted_peak_price = current_price * combined_factor
        
        # Ensure within realistic bounds
        predicted_peak_price = min(predicted_peak_price, max_price)
        predicted_peak_price = max(predicted_peak_price, current_price * 1.05)  # At least 5% increase
        
        # Calculate low price (for completeness)
        predicted_low_price = current_price * 0.85
        predicted_low_price = max(predicted_low_price, min_price)
        
        # Calculate increase
        price_increase = predicted_peak_price - current_price
        price_increase_percent = (price_increase / current_price) * 100 if current_price > 0 else 0
        
        # Find best selling period
        best_selling_dates = self._calculate_selling_window(current_month, peak_months)
        
        explanation = f"""
Price Prediction Analysis:
- Current Price: ₹{current_price:.2f}/quintal
- Supply Factor: {supply_factor}x ({supply_level} supply)
- Demand Factor: {demand_factor}x ({demand_level} demand)
- Peak Season Factor: {peak_seasonal_factor:.2f}x
- Predicted Peak Price: ₹{predicted_peak_price:.2f}/quintal
- Expected Increase: ₹{price_increase:.2f} ({price_increase_percent:.1f}%)
- Best Selling Period: {best_selling_dates['start'].strftime('%B %Y')}
        """.strip()
        
        return {
            'current_price': round(current_price, 2),
            'predicted_peak_price': round(predicted_peak_price, 2),
            'predicted_low_price': round(predicted_low_price, 2),
            'price_increase': round(price_increase, 2),
            'price_increase_percent': round(price_increase_percent, 2),
            'best_selling_start': best_selling_dates['start'],
            'best_selling_end': best_selling_dates['end'],
            'confidence': 75.0,
            'method': 'statistical',
            'explanation': explanation,
            'peak_months': peak_months,
            'factors': {
                'supply': supply_factor,
                'demand': demand_factor,
                'seasonal': round(peak_seasonal_factor, 2)
            }
        }
    
    def _calculate_selling_window(self, current_month, peak_months):
        """
        Calculate optimal selling window based on peak months
        
        Args:
            current_month (int): Current month
            peak_months (list): List of peak price months
        
        Returns:
            dict: Start and end dates for selling window
        """
        current_date = datetime.now()
        
        # Find next peak month
        next_peak_month = None
        for offset in range(12):
            check_month = ((current_month - 1 + offset) % 12) + 1
            if check_month in peak_months:
                next_peak_month = check_month
                break
        
        if next_peak_month is None:
            next_peak_month = peak_months[0] if peak_months else current_month
        
        # Calculate months to wait
        if next_peak_month >= current_month:
            months_to_wait = next_peak_month - current_month
        else:
            months_to_wait = (12 - current_month) + next_peak_month
        
        # Calculate dates (approximate 30 days per month)
        days_to_wait = months_to_wait * 30
        start_date = current_date + timedelta(days=days_to_wait)
        end_date = start_date + timedelta(days=14)  # 2-week selling window
        
        return {
            'start': start_date,
            'end': end_date,
            'months_to_wait': months_to_wait
        }
    
    def train_model(self, X_train, y_train):
        """
        Train the price prediction model
        
        Args:
            X_train: Training features
            y_train: Training labels (price values)
        
        Returns:
            dict: Training results
        """
        try:
            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X_train)
            
            # Train Random Forest model
            self.model = RandomForestRegressor(
                n_estimators=150,
                max_depth=15,
                random_state=42,
                n_jobs=-1
            )
            self.model.fit(X_scaled, y_train)
            
            # Save model
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            
            # Calculate R² score
            train_score = self.model.score(X_scaled, y_train)
            
            return {
                'status': 'success',
                'r2_score': train_score,
                'model_path': self.model_path,
                'n_samples': len(X_train),
                'n_features': X_train.shape[1]
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
