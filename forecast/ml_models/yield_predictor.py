"""
Yield Prediction Model
Uses machine learning to predict crop yield based on multiple factors
Considers weather, soil, disease, and agricultural practices
"""

import os
import numpy as np
import pickle
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import joblib


class YieldPredictor:
    """
    Crop Yield Prediction using Machine Learning
    
    Predicts crop yield (in quintals) based on:
    - Crop type
    - Land area (acres)
    - Weather conditions (rainfall, temperature, humidity)
    - Disease severity
    - Soil quality
    - Farming practices
    """
    
    def __init__(self, model_path=None):
        """
        Initialize the yield predictor
        
        Args:
            model_path (str): Path to pre-trained model file
        """
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), 
            'trained_models', 
            'yield_model.pkl'
        )
        self.scaler_path = os.path.join(
            os.path.dirname(__file__), 
            'trained_models', 
            'yield_scaler.pkl'
        )
        
        # Base yield data for Krishna District crops (quintals per acre)
        self.base_yield_data = {
            'paddy': {
                'average': 25.0,
                'min': 15.0,
                'max': 35.0,
                'optimal_temp': (25, 35),
                'optimal_rainfall': (1200, 2000),  # mm annually
                'optimal_humidity': (70, 85)
            },
            'mango': {
                'average': 30.0,
                'min': 20.0,
                'max': 50.0,
                'optimal_temp': (24, 30),
                'optimal_rainfall': (750, 2500),
                'optimal_humidity': (60, 75)
            },
            'chillies': {
                'average': 12.0,
                'min': 7.0,
                'max': 18.0,
                'optimal_temp': (20, 30),
                'optimal_rainfall': (600, 1250),
                'optimal_humidity': (60, 70)
            },
            'cotton': {
                'average': 8.0,
                'min': 5.0,
                'max': 12.0,
                'optimal_temp': (21, 30),
                'optimal_rainfall': (500, 1000),
                'optimal_humidity': (50, 70)
            },
            'turmeric': {
                'average': 20.0,
                'min': 12.0,
                'max': 30.0,
                'optimal_temp': (20, 30),
                'optimal_rainfall': (1500, 2250),
                'optimal_humidity': (70, 80)
            },
            'sugarcane': {
                'average': 250.0,
                'min': 180.0,
                'max': 350.0,
                'optimal_temp': (21, 27),
                'optimal_rainfall': (1500, 2500),
                'optimal_humidity': (70, 80)
            },
            'banana': {
                'average': 150.0,
                'min': 100.0,
                'max': 200.0,
                'optimal_temp': (15, 35),
                'optimal_rainfall': (1800, 2700),
                'optimal_humidity': (75, 85)
            },
            'tomato': {
                'average': 100.0,
                'min': 60.0,
                'max': 150.0,
                'optimal_temp': (18, 27),
                'optimal_rainfall': (600, 1300),
                'optimal_humidity': (60, 70)
            },
            'okra': {
                'average': 40.0,
                'min': 25.0,
                'max': 60.0,
                'optimal_temp': (25, 35),
                'optimal_rainfall': (600, 1000),
                'optimal_humidity': (60, 70)
            },
            'brinjal': {
                'average': 80.0,
                'min': 50.0,
                'max': 120.0,
                'optimal_temp': (22, 30),
                'optimal_rainfall': (600, 1000),
                'optimal_humidity': (65, 75)
            },
            'maize': {
                'average': 15.0,
                'min': 10.0,
                'max': 25.0,
                'optimal_temp': (21, 27),
                'optimal_rainfall': (600, 1200),
                'optimal_humidity': (60, 70)
            },
            'groundnut': {
                'average': 10.0,
                'min': 6.0,
                'max': 15.0,
                'optimal_temp': (25, 30),
                'optimal_rainfall': (500, 1250),
                'optimal_humidity': (50, 70)
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
                print(f"Yield prediction model loaded from {self.model_path}")
            
            if os.path.exists(self.scaler_path):
                self.scaler = joblib.load(self.scaler_path)
                print(f"Scaler loaded from {self.scaler_path}")
        except Exception as e:
            print(f"Could not load pre-trained model: {e}")
            self.model = None
            self.scaler = None
    
    def _encode_crop(self, crop_type):
        """
        Encode crop type as numerical features
        
        Args:
            crop_type (str): Crop name
        
        Returns:
            int: Crop code
        """
        crop_codes = {
            'paddy': 1, 'mango': 2, 'chillies': 3, 'cotton': 4,
            'turmeric': 5, 'sugarcane': 6, 'banana': 7, 'tomato': 8,
            'okra': 9, 'brinjal': 10, 'maize': 11, 'groundnut': 12
        }
        return crop_codes.get(crop_type.lower(), 0)
    
    def _encode_severity(self, severity):
        """
        Encode disease severity as numerical value
        
        Args:
            severity (str): Severity level
        
        Returns:
            int: Severity code (0=low, 1=medium, 2=high)
        """
        severity_map = {'low': 0, 'medium': 1, 'high': 2}
        return severity_map.get(severity.lower(), 0)
    
    def prepare_features(self, crop_type, acres, rainfall, temperature, 
                        humidity, disease_severity='low', crop_age_days=0,
                        soil_quality='medium', irrigation='moderate'):
        """
        Prepare feature vector for prediction
        
        Args:
            crop_type (str): Type of crop
            acres (float): Land area in acres
            rainfall (float): Rainfall in mm
            temperature (float): Temperature in Celsius
            humidity (float): Humidity percentage
            disease_severity (str): Disease severity level
            crop_age_days (int): Days since sowing
            soil_quality (str): Soil quality (poor/medium/good)
            irrigation (str): Irrigation level (poor/moderate/good)
        
        Returns:
            np.array: Feature vector
        """
        # Encode categorical variables
        crop_code = self._encode_crop(crop_type)
        severity_code = self._encode_severity(disease_severity)
        
        soil_codes = {'poor': 0, 'medium': 1, 'good': 2}
        soil_code = soil_codes.get(soil_quality.lower(), 1)
        
        irrigation_codes = {'poor': 0, 'moderate': 1, 'good': 2}
        irrigation_code = irrigation_codes.get(irrigation.lower(), 1)
        
        # Create feature vector
        features = np.array([
            crop_code,
            acres,
            rainfall,
            temperature,
            humidity,
            severity_code,
            crop_age_days,
            soil_code,
            irrigation_code
        ])
        
        return features
    
    def predict(self, crop_type, acres, rainfall, temperature, humidity,
                disease_severity='low', disease_yield_loss=0, crop_age_days=0,
                soil_quality='medium', irrigation='moderate'):
        """
        Predict crop yield
        
        Args:
            crop_type (str): Type of crop
            acres (float): Land area in acres
            rainfall (float): Rainfall in mm (monthly)
            temperature (float): Temperature in Celsius
            humidity (float): Humidity percentage
            disease_severity (str): Disease severity level
            disease_yield_loss (float): Yield loss from disease (%)
            crop_age_days (int): Days since sowing
            soil_quality (str): Soil quality
            irrigation (str): Irrigation level
        
        Returns:
            dict: Prediction results
                - predicted_yield: Predicted yield in quintals
                - base_yield: Base yield without factors
                - weather_factor: Weather impact multiplier
                - disease_loss: Yield loss from disease
                - confidence: Prediction confidence (0-100)
                - explanation: Detailed breakdown
        """
        
        # Get base yield data
        crop_data = self.base_yield_data.get(
            crop_type.lower(),
            {'average': 15.0, 'min': 10.0, 'max': 25.0,
             'optimal_temp': (20, 30), 'optimal_rainfall': (500, 1500),
             'optimal_humidity': (60, 75)}
        )
        
        base_yield_per_acre = crop_data['average']
        base_total_yield = base_yield_per_acre * acres
        
        # Try ML prediction first
        if self.model is not None:
            try:
                features = self.prepare_features(
                    crop_type, acres, rainfall, temperature, humidity,
                    disease_severity, crop_age_days, soil_quality, irrigation
                )
                features_reshaped = features.reshape(1, -1)
                
                # Scale features if scaler available
                if self.scaler is not None:
                    features_scaled = self.scaler.transform(features_reshaped)
                else:
                    features_scaled = features_reshaped
                
                # Predict
                ml_prediction = self.model.predict(features_scaled)[0]
                
                # Apply disease loss
                final_yield = ml_prediction * (1 - disease_yield_loss / 100)
                final_yield = max(0, final_yield)
                
                return {
                    'predicted_yield': round(final_yield, 2),
                    'base_yield': round(base_total_yield, 2),
                    'ml_prediction': round(ml_prediction, 2),
                    'disease_loss_percent': disease_yield_loss,
                    'disease_loss_amount': round(ml_prediction * (disease_yield_loss / 100), 2),
                    'confidence': 85.0,
                    'method': 'machine_learning',
                    'explanation': f'ML model predicted {ml_prediction:.2f} quintals. After {disease_yield_loss}% disease loss: {final_yield:.2f} quintals.'
                }
                
            except Exception as e:
                print(f"ML prediction failed: {e}")
                # Fall through to physics-based model
        
        # Physics-based prediction (fallback)
        return self._physics_based_prediction(
            crop_type, crop_data, base_total_yield, acres,
            rainfall, temperature, humidity, disease_severity,
            disease_yield_loss
        )
    
    def _physics_based_prediction(self, crop_type, crop_data, base_total_yield, 
                                   acres, rainfall, temperature, humidity,
                                   disease_severity, disease_yield_loss):
        """
        Physics-based yield prediction using agricultural science
        
        Returns:
            dict: Prediction results
        """
        # Calculate weather factors
        temp_optimal = crop_data['optimal_temp']
        rain_optimal = crop_data['optimal_rainfall']
        humid_optimal = crop_data['optimal_humidity']
        
        # Temperature factor
        if temp_optimal[0] <= temperature <= temp_optimal[1]:
            temp_factor = 1.1
        elif temperature < temp_optimal[0] - 10 or temperature > temp_optimal[1] + 10:
            temp_factor = 0.6
        else:
            temp_factor = 0.85
        
        # Rainfall factor (convert monthly to annual estimate)
        annual_rainfall_estimate = rainfall * 12
        if rain_optimal[0] <= annual_rainfall_estimate <= rain_optimal[1]:
            rain_factor = 1.15
        elif annual_rainfall_estimate < rain_optimal[0] * 0.5:
            rain_factor = 0.5
        elif annual_rainfall_estimate > rain_optimal[1] * 1.5:
            rain_factor = 0.7
        else:
            rain_factor = 0.9
        
        # Humidity factor
        if humid_optimal[0] <= humidity <= humid_optimal[1]:
            humid_factor = 1.1
        elif humidity < humid_optimal[0] - 20 or humidity > humid_optimal[1] + 20:
            humid_factor = 0.7
        else:
            humid_factor = 0.9
        
        # Combined weather factor
        weather_factor = (temp_factor + rain_factor + humid_factor) / 3
        weather_factor = max(0.5, min(1.3, weather_factor))
        
        # Apply weather factor
        yield_after_weather = base_total_yield * weather_factor
        
        # Apply disease loss
        disease_loss_amount = yield_after_weather * (disease_yield_loss / 100)
        final_yield = yield_after_weather - disease_loss_amount
        final_yield = max(0, final_yield)
        
        explanation = f"""
Yield Prediction (Physics-Based Model):
- Base Yield: {base_total_yield:.2f} quintals ({acres} acres × {crop_data['average']} q/acre)
- Weather Factor: {weather_factor:.2f}x
  • Temperature: {temp_factor:.2f}x ({temperature}°C, optimal: {temp_optimal[0]}-{temp_optimal[1]}°C)
  • Rainfall: {rain_factor:.2f}x ({rainfall}mm/month, optimal: {rain_optimal[0]/12:.0f}-{rain_optimal[1]/12:.0f}mm/month)
  • Humidity: {humid_factor:.2f}x ({humidity}%, optimal: {humid_optimal[0]}-{humid_optimal[1]}%)
- After Weather: {yield_after_weather:.2f} quintals
- Disease Loss: {disease_yield_loss}% = {disease_loss_amount:.2f} quintals
- Final Predicted Yield: {final_yield:.2f} quintals
        """.strip()
        
        return {
            'predicted_yield': round(final_yield, 2),
            'base_yield': round(base_total_yield, 2),
            'weather_factor': round(weather_factor, 2),
            'yield_after_weather': round(yield_after_weather, 2),
            'disease_loss_percent': disease_yield_loss,
            'disease_loss_amount': round(disease_loss_amount, 2),
            'confidence': 75.0,
            'method': 'physics_based',
            'explanation': explanation,
            'factors': {
                'temperature': round(temp_factor, 2),
                'rainfall': round(rain_factor, 2),
                'humidity': round(humid_factor, 2)
            }
        }
    
    def train_model(self, X_train, y_train):
        """
        Train the yield prediction model
        
        Args:
            X_train: Training features
            y_train: Training labels (yield values)
        
        Returns:
            dict: Training results
        """
        try:
            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X_train)
            
            # Train Gradient Boosting model
            self.model = GradientBoostingRegressor(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
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
