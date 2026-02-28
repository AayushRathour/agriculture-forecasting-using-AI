"""
Data Preprocessing Utilities for ML Models
Handles data cleaning, feature engineering, and preparation for model training
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


class DataPreprocessor:
    """
    Utility class for preprocessing agricultural data
    """
    
    @staticmethod
    def generate_synthetic_disease_data(n_samples=1000):
        """
        Generate synthetic disease detection training data
        
        Args:
            n_samples (int): Number of samples to generate
        
        Returns:
            tuple: (features, labels) for training
        """
        np.random.seed(42)
        
        diseases = [
            'blast', 'brown_spot', 'sheath_blight', 'bacterial_leaf_blight',
            'anthracnose', 'powdery_mildew', 'bacterial_wilt', 'healthy'
        ]
        
        features = []
        labels = []
        
        for _ in range(n_samples):
            # Random disease
            disease = np.random.choice(diseases)
            
            # Generate features based on disease characteristics
            if disease == 'healthy':
                # Healthy: Green dominant, low variation
                r = np.random.normal(80, 15)
                g = np.random.normal(140, 20)
                b = np.random.normal(70, 15)
                r_std = np.random.normal(20, 5)
                g_std = np.random.normal(25, 5)
                b_std = np.random.normal(20, 5)
            elif 'blast' in disease or 'spot' in disease:
                # Dark spots: Lower overall values
                r = np.random.normal(70, 20)
                g = np.random.normal(60, 20)
                b = np.random.normal(50, 15)
                r_std = np.random.normal(35, 10)
                g_std = np.random.normal(35, 10)
                b_std = np.random.normal(30, 10)
            elif 'anthracnose' in disease or 'blight' in disease:
                # Brownish discoloration
                r = np.random.normal(120, 25)
                g = np.random.normal(90, 20)
                b = np.random.normal(60, 15)
                r_std = np.random.normal(40, 10)
                g_std = np.random.normal(35, 10)
                b_std = np.random.normal(30, 8)
            else:
                # Other diseases: Variable patterns
                r = np.random.normal(100, 30)
                g = np.random.normal(100, 30)
                b = np.random.normal(80, 25)
                r_std = np.random.normal(30, 10)
                g_std = np.random.normal(30, 10)
                b_std = np.random.normal(25, 8)
            
            # Generate histogram features (simplified)
            r_hist = np.random.dirichlet(np.ones(16))
            g_hist = np.random.dirichlet(np.ones(16))
            b_hist = np.random.dirichlet(np.ones(16))
            
            # Combine features
            feature_vector = np.concatenate([
                [r, g, b, r_std, g_std, b_std],
                r_hist, g_hist, b_hist
            ])
            
            features.append(feature_vector)
            labels.append(disease)
        
        return np.array(features), np.array(labels)
    
    @staticmethod
    def generate_synthetic_yield_data(n_samples=1000):
        """
        Generate synthetic yield prediction training data
        
        Args:
            n_samples (int): Number of samples to generate
        
        Returns:
            tuple: (features, yields) for training
        """
        np.random.seed(42)
        
        crops = ['paddy', 'mango', 'chillies', 'cotton', 'tomato', 
                'banana', 'turmeric', 'okra', 'brinjal']
        
        base_yields = {
            'paddy': 25, 'mango': 30, 'chillies': 12, 'cotton': 8,
            'tomato': 100, 'banana': 150, 'turmeric': 20, 
            'okra': 40, 'brinjal': 80
        }
        
        features = []
        yields = []
        
        for _ in range(n_samples):
            # Random crop
            crop = np.random.choice(crops)
            crop_code = crops.index(crop) + 1
            
            # Random features
            acres = np.random.uniform(0.5, 10.0)
            rainfall = np.random.uniform(30, 200)
            temperature = np.random.uniform(18, 40)
            humidity = np.random.uniform(40, 95)
            disease_severity = np.random.randint(0, 3)  # 0=low, 1=medium, 2=high
            crop_age = np.random.randint(30, 150)
            soil_quality = np.random.randint(0, 3)
            irrigation = np.random.randint(0, 3)
            
            # Calculate yield based on features
            base_yield = base_yields[crop]
            
            # Weather effects
            if 25 <= temperature <= 32:
                temp_factor = 1.1
            elif temperature < 20 or temperature > 38:
                temp_factor = 0.7
            else:
                temp_factor = 0.9
            
            if 60 <= rainfall <= 120:
                rain_factor = 1.1
            elif rainfall < 40 or rainfall > 150:
                rain_factor = 0.7
            else:
                rain_factor = 0.95
            
            if 60 <= humidity <= 80:
                humid_factor = 1.05
            else:
                humid_factor = 0.9
            
            # Disease and soil effects
            disease_factor = 1.0 - (disease_severity * 0.15)
            soil_factor = 0.85 + (soil_quality * 0.1)
            irrigation_factor = 0.9 + (irrigation * 0.1)
            
            # Calculate final yield
            yield_value = (base_yield * acres * temp_factor * rain_factor * 
                          humid_factor * disease_factor * soil_factor * 
                          irrigation_factor)
            
            # Add some noise
            yield_value *= np.random.uniform(0.85, 1.15)
            yield_value = max(0, yield_value)
            
            features.append([
                crop_code, acres, rainfall, temperature, humidity,
                disease_severity, crop_age, soil_quality, irrigation
            ])
            yields.append(yield_value)
        
        return np.array(features), np.array(yields)
    
    @staticmethod
    def generate_synthetic_price_data(n_samples=1000):
        """
        Generate synthetic price prediction training data
        
        Args:
            n_samples (int): Number of samples to generate
        
        Returns:
            tuple: (features, prices) for training
        """
        np.random.seed(42)
        
        crops = ['paddy', 'mango', 'chillies', 'cotton', 'tomato', 
                'banana', 'turmeric', 'okra', 'brinjal']
        
        base_prices = {
            'paddy': 2200, 'mango': 3200, 'chillies': 9000, 'cotton': 7200,
            'tomato': 1400, 'banana': 1800, 'turmeric': 9500, 
            'okra': 2200, 'brinjal': 2000
        }
        
        features = []
        prices = []
        
        for _ in range(n_samples):
            # Random crop
            crop = np.random.choice(crops)
            crop_code = crops.index(crop) + 1
            
            # Random features
            current_price = base_prices[crop] * np.random.uniform(0.8, 1.2)
            month = np.random.randint(1, 13)
            supply = np.random.randint(0, 3)  # 0=low, 1=normal, 2=high
            demand = np.random.randint(0, 3)
            
            # Calculate future price
            # Seasonal variation
            seasonal_factor = 1.0 + np.sin(month * np.pi / 6) * 0.15
            
            # Supply-demand
            if supply == 0:  # Low supply
                supply_factor = 1.2
            elif supply == 2:  # High supply
                supply_factor = 0.85
            else:
                supply_factor = 1.0
            
            if demand == 2:  # High demand
                demand_factor = 1.15
            elif demand == 0:  # Low demand
                demand_factor = 0.9
            else:
                demand_factor = 1.0
            
            # Calculate peak price
            peak_price = (current_price * seasonal_factor * 
                         supply_factor * demand_factor)
            
            # Add noise
            peak_price *= np.random.uniform(0.95, 1.15)
            
            features.append([crop_code, current_price, month, supply, demand])
            prices.append(peak_price)
        
        return np.array(features), np.array(prices)
    
    @staticmethod
    def clean_weather_data(weather_df):
        """
        Clean and validate weather data
        
        Args:
            weather_df: DataFrame with weather data
        
        Returns:
            DataFrame: Cleaned weather data
        """
        # Remove duplicates
        weather_df = weather_df.drop_duplicates()
        
        # Handle missing values
        weather_df = weather_df.fillna(method='ffill').fillna(method='bfill')
        
        # Validate ranges
        weather_df.loc[weather_df['temperature'] < -10, 'temperature'] = weather_df['temperature'].median()
        weather_df.loc[weather_df['temperature'] > 50, 'temperature'] = weather_df['temperature'].median()
        
        weather_df.loc[weather_df['rainfall'] < 0, 'rainfall'] = 0
        weather_df.loc[weather_df['rainfall'] > 500, 'rainfall'] = weather_df['rainfall'].median()
        
        weather_df.loc[weather_df['humidity'] < 0, 'humidity'] = 0
        weather_df.loc[weather_df['humidity'] > 100, 'humidity'] = 100
        
        return weather_df
    
    @staticmethod
    def engineer_features(farmer_data, weather_data, price_data, disease_data):
        """
        Engineer features for ML models
        
        Args:
            farmer_data: Farmer records
            weather_data: Weather records
            price_data: Market price records
            disease_data: Disease records
        
        Returns:
            DataFrame: Engineered features
        """
        # This would combine and transform data from multiple sources
        # Implementation depends on actual data structure
        pass
