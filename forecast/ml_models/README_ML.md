# Machine Learning Models Documentation

## Overview

This agricultural forecasting system uses three integrated ML models:

### 1. Disease Detection Model (`disease_detector.py`)
- **Type**: Image Classification
- **Algorithm**: Random Forest Classifier
- **Input**: Crop images (RGB)
- **Output**: Disease name, severity, yield loss percentage
- **Features**: 
  - Color statistics (mean, std for R, G, B channels)
  - Color histograms (16 bins per channel)
  - Total: 54 features
- **Fallback**: Rule-based color analysis

### 2. Yield Prediction Model (`yield_predictor.py`)
- **Type**: Regression
- **Algorithm**: Gradient Boosting Regressor
- **Input Features**:
  - Crop type (encoded)
  - Land area (acres)
  - Weather data (rainfall, temperature, humidity)
  - Disease severity
  - Crop age (days)
  - Soil quality
  - Irrigation level
- **Output**: Predicted yield in quintals
- **Fallback**: Physics-based agricultural model

### 3. Price Prediction Model (`price_predictor.py`)
- **Type**: Time Series / Regression
- **Algorithm**: Random Forest Regressor
- **Input Features**:
  - Crop type
  - Current price
  - Month (seasonal patterns)
  - Supply level
  - Demand level
- **Output**: Peak price, optimal selling window
- **Fallback**: Statistical seasonal analysis

## Model Training

### Quick Start

Train all models with synthetic data:

```bash
python manage.py train_models
```

### Train Specific Models

```bash
# Train only disease detection
python manage.py train_models --model disease

# Train only yield prediction
python manage.py train_models --model yield

# Train only price prediction
python manage.py train_models --model price

# Train with more samples
python manage.py train_models --samples 5000
```

### Model Locations

Trained models are saved in:
```
forecast/ml_models/trained_models/
├── disease_model.pkl
├── disease_label_encoder.pkl
├── yield_model.pkl
├── yield_scaler.pkl
├── price_model.pkl
└── price_scaler.pkl
```

## How Models Work

### Disease Detection Workflow

1. **Image Upload**: Farmer uploads crop image
2. **Feature Extraction**: Extract color and texture features
3. **ML Prediction**: If trained model exists, use it
4. **Fallback**: Use rule-based detection if ML unavailable
5. **Result**: Disease name, severity (low/medium/high), yield loss %

**Supported Crops**:
- Paddy, Mango, Chillies, Cotton, Tomato, Banana, etc.

**Detected Diseases**:
- Paddy: Blast, Brown Spot, Bacterial Leaf Blight, etc.
- Mango: Anthracnose, Powdery Mildew, Bacterial Canker
- Tomato: Early Blight, Late Blight, Bacterial Spot
- And more...

### Yield Prediction Workflow

1. **Data Collection**: Get farmer inputs + weather data
2. **Feature Preparation**: Encode categorical variables
3. **ML Prediction**: Use trained model if available
4. **Factor Analysis**: Calculate weather, disease, soil impacts
5. **Fallback**: Physics-based agricultural model
6. **Result**: Predicted yield, confidence score, breakdown

**Key Factors**:
- Base yield per acre (crop-specific)
- Weather impact (rainfall, temperature, humidity)
- Disease loss (from disease detector)
- Soil and irrigation quality

### Price Prediction Workflow

1. **Historical Analysis**: Check recent prices from database
2. **Seasonal Patterns**: Identify peak and low seasons
3. **ML Prediction**: Use model for peak price
4. **Supply-Demand**: Factor in market conditions
5. **Fallback**: Statistical seasonal model
6. **Result**: Peak price, selling window, increase %

**Peak Seasons** (Examples):
- Paddy: November-January
- Mango: March-April (pre-harvest)
- Chillies: December-January

## Integration with Django Views

### farmer_input view
```python
# When image is uploaded, automatically detect disease
detector = get_disease_detector()
detection_result = detector.predict(image_path, crop_type)
# Updates DiseaseRecord with ML predictions
```

### result view
```python
# Yield prediction using ML
yield_predictor = get_yield_predictor()
yield_prediction = yield_predictor.predict(...)

# Price prediction using ML
price_predictor = get_price_predictor()
price_prediction = price_predictor.predict(...)

# Final recommendation combines both
```

## Model Performance

### Expected Accuracy (with 1000+ training samples)

- **Disease Detection**: 75-85% accuracy
- **Yield Prediction**: R² score 0.7-0.85
- **Price Prediction**: R² score 0.65-0.80

### Improving Accuracy

1. **Collect Real Data**:
   - Actual crop images with labeled diseases
   - Historical yield data with weather records
   - Market price time series

2. **Retrain Models**:
   ```python
   # In Django shell or custom script
   from forecast.ml_models.disease_detector import DiseaseDetector
   
   detector = DiseaseDetector()
   # Prepare your real data: X_train, y_train
   detector.train_model(X_train, y_train)
   ```

3. **Feature Engineering**:
   - Add more weather features
   - Include soil test data
   - Add market trend indicators

## Advanced Usage

### Using Models Programmatically

```python
from forecast.ml_models.disease_detector import DiseaseDetector
from forecast.ml_models.yield_predictor import YieldPredictor
from forecast.ml_models.price_predictor import PricePredictor

# Disease detection
detector = DiseaseDetector()
result = detector.predict('path/to/image.jpg', crop_type='paddy')
print(f"Disease: {result['disease_name']}")
print(f"Severity: {result['severity']}")
print(f"Yield Loss: {result['yield_loss']}%")

# Yield prediction
yield_pred = YieldPredictor()
prediction = yield_pred.predict(
    crop_type='paddy',
    acres=5.0,
    rainfall=80,
    temperature=28,
    humidity=75,
    disease_severity='medium'
)
print(f"Predicted Yield: {prediction['predicted_yield']} quintals")

# Price prediction
price_pred = PricePredictor()
price_result = price_pred.predict(
    crop_type='paddy',
    current_price=2200
)
print(f"Peak Price: ₹{price_result['predicted_peak_price']}")
```

## Troubleshooting

### Models Not Loading
- Check if `trained_models/` folder exists
- Run `python manage.py train_models` to create models
- Models will fall back to rule-based/statistical methods

### Low Accuracy
- Generate more training samples: `--samples 5000`
- Collect and train with real data
- Check feature engineering in preprocessing

### Memory Issues
- Reduce n_estimators in Random Forest
- Use smaller training samples
- Consider ensemble methods

## Future Enhancements

### Planned Improvements

1. **Deep Learning for Disease Detection**
   - CNN-based image classification
   - Transfer learning (ResNet, VGG)
   - Higher accuracy (90%+)

2. **Time Series for Price Prediction**
   - LSTM/GRU models
   - ARIMA for seasonal patterns
   - Real-time market data integration

3. **Advanced Yield Prediction**
   - Satellite imagery analysis
   - Multi-modal inputs (soil sensors)
   - Weather forecast integration

4. **Recommendation System**
   - Collaborative filtering
   - Crop rotation suggestions
   - Personalized advice based on history

## References

- Scikit-learn Documentation: https://scikit-learn.org/
- Agricultural ML Research Papers
- Krishna District Agricultural Data

---

**Last Updated**: February 28, 2026
**Version**: 2.0
**Maintainer**: Bhoomi Puthra Development Team
