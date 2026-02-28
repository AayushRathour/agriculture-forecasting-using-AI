"""
Django management command to train ML models
Generates synthetic training data and trains all three models
"""

from django.core.management.base import BaseCommand
from forecast.ml_models.disease_detector import DiseaseDetector
from forecast.ml_models.yield_predictor import YieldPredictor
from forecast.ml_models.price_predictor import PricePredictor
from forecast.ml_models.data_preprocessing import DataPreprocessor
import os


class Command(BaseCommand):
    help = 'Train all machine learning models for crop forecasting'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--samples',
            type=int,
            default=1000,
            help='Number of synthetic samples to generate for training'
        )
        parser.add_argument(
            '--model',
            type=str,
            choices=['disease', 'yield', 'price', 'all'],
            default='all',
            help='Which model to train (default: all)'
        )
    
    def handle(self, *args, **options):
        n_samples = options['samples']
        model_choice = options['model']
        
        self.stdout.write(self.style.SUCCESS(
            f'\n{"="*60}\n'
            f'Training ML Models for Agricultural Forecasting\n'
            f'{"="*60}\n'
        ))
        
        # Create trained_models directory
        models_dir = os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            'ml_models',
            'trained_models'
        )
        os.makedirs(models_dir, exist_ok=True)
        
        # Train Disease Detection Model
        if model_choice in ['disease', 'all']:
            self.stdout.write(self.style.WARNING('\n1. Training Disease Detection Model...'))
            self.train_disease_model(n_samples)
        
        # Train Yield Prediction Model
        if model_choice in ['yield', 'all']:
            self.stdout.write(self.style.WARNING('\n2. Training Yield Prediction Model...'))
            self.train_yield_model(n_samples)
        
        # Train Price Prediction Model
        if model_choice in ['price', 'all']:
            self.stdout.write(self.style.WARNING('\n3. Training Price Prediction Model...'))
            self.train_price_model(n_samples)
        
        self.stdout.write(self.style.SUCCESS(
            f'\n{"="*60}\n'
            f'✅ Model Training Complete!\n'
            f'{"="*60}\n'
        ))
    
    def train_disease_model(self, n_samples):
        """Train the disease detection model"""
        try:
            # Generate synthetic training data
            self.stdout.write('   Generating synthetic disease data...')
            X_train, y_train = DataPreprocessor.generate_synthetic_disease_data(n_samples)
            
            self.stdout.write(f'   Generated {len(X_train)} training samples')
            self.stdout.write(f'   Features shape: {X_train.shape}')
            self.stdout.write(f'   Unique diseases: {len(set(y_train))}')
            
            # Train model
            self.stdout.write('   Training Random Forest classifier...')
            detector = DiseaseDetector()
            result = detector.train_model(X_train, y_train)
            
            if result['status'] == 'success':
                self.stdout.write(self.style.SUCCESS(
                    f'   ✅ Disease model trained successfully!\n'
                    f'      - Accuracy: {result["accuracy"]:.2%}\n'
                    f'      - Samples: {result["n_samples"]}\n'
                    f'      - Classes: {result["n_classes"]}\n'
                    f'      - Model saved to: {result["model_path"]}'
                ))
            else:
                self.stdout.write(self.style.ERROR(
                    f'   ❌ Training failed: {result["error"]}'
                ))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Error: {str(e)}'))
    
    def train_yield_model(self, n_samples):
        """Train the yield prediction model"""
        try:
            # Generate synthetic training data
            self.stdout.write('   Generating synthetic yield data...')
            X_train, y_train = DataPreprocessor.generate_synthetic_yield_data(n_samples)
            
            self.stdout.write(f'   Generated {len(X_train)} training samples')
            self.stdout.write(f'   Features shape: {X_train.shape}')
            self.stdout.write(f'   Yield range: {y_train.min():.2f} - {y_train.max():.2f} quintals')
            
            # Train model
            self.stdout.write('   Training Gradient Boosting regressor...')
            predictor = YieldPredictor()
            result = predictor.train_model(X_train, y_train)
            
            if result['status'] == 'success':
                self.stdout.write(self.style.SUCCESS(
                    f'   ✅ Yield model trained successfully!\n'
                    f'      - R² Score: {result["r2_score"]:.4f}\n'
                    f'      - Samples: {result["n_samples"]}\n'
                    f'      - Features: {result["n_features"]}\n'
                    f'      - Model saved to: {result["model_path"]}'
                ))
            else:
                self.stdout.write(self.style.ERROR(
                    f'   ❌ Training failed: {result["error"]}'
                ))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Error: {str(e)}'))
    
    def train_price_model(self, n_samples):
        """Train the price prediction model"""
        try:
            # Generate synthetic training data
            self.stdout.write('   Generating synthetic price data...')
            X_train, y_train = DataPreprocessor.generate_synthetic_price_data(n_samples)
            
            self.stdout.write(f'   Generated {len(X_train)} training samples')
            self.stdout.write(f'   Features shape: {X_train.shape}')
            self.stdout.write(f'   Price range: ₹{y_train.min():.2f} - ₹{y_train.max():.2f} per quintal')
            
            # Train model
            self.stdout.write('   Training Random Forest regressor...')
            predictor = PricePredictor()
            result = predictor.train_model(X_train, y_train)
            
            if result['status'] == 'success':
                self.stdout.write(self.style.SUCCESS(
                    f'   ✅ Price model trained successfully!\n'
                    f'      - R² Score: {result["r2_score"]:.4f}\n'
                    f'      - Samples: {result["n_samples"]}\n'
                    f'      - Features: {result["n_features"]}\n'
                    f'      - Model saved to: {result["model_path"]}'
                ))
            else:
                self.stdout.write(self.style.ERROR(
                    f'   ❌ Training failed: {result["error"]}'
                ))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Error: {str(e)}'))
