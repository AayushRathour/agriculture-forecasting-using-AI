"""
Database models for the Crop Forecasting System
These models store farmer data, crop health, weather, market prices, and predictions
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


# ========================================
# Choice Fields - Krishna District Specific
# ========================================

MANDAL_CHOICES = [
    ('machilipatnam', 'Machilipatnam'),
    ('gudivada', 'Gudivada'),
    ('vuyyur', 'Vuyyur'),
]

# 10 Major Crops in Krishna District
CROP_CHOICES = [
    ('paddy', 'Paddy (Rice)'),
    ('mango', 'Mango'),
    ('chillies', 'Chillies'),
    ('cotton', 'Cotton'),
    ('turmeric', 'Turmeric'),
    ('sugarcane', 'Sugarcane'),
    ('banana', 'Banana'),
    ('tomato', 'Tomato'),
    ('okra', 'Okra (Bhendi)'),
    ('brinjal', 'Brinjal (Eggplant)'),
]

SEVERITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
]

RECOMMENDATION_CHOICES = [
    ('store', 'STORE - Wait for Better Price'),
    ('sell', 'SELL NOW - Immediate Sale Recommended'),
]


# ========================================
# Model 1: Farmer (Main Input Data)
# ========================================

class Farmer(models.Model):
    """
    Stores farmer's basic information and crop details
    This is the primary input from the farmer
    """
    # Location Information
    mandal = models.CharField(
        max_length=50,
        choices=MANDAL_CHOICES,
        verbose_name="Mandal (మండలం)",
        help_text="Select your mandal/region"
    )
    
    village = models.CharField(
        max_length=100,
        verbose_name="Village (గ్రామం)",
        help_text="Enter your village name"
    )
    
    # Crop Information
    crop = models.CharField(
        max_length=50,
        choices=CROP_CHOICES,
        verbose_name="Crop Type (పంట రకం)",
        help_text="Select the crop you are growing"
    )
    
    acres = models.FloatField(
        validators=[MinValueValidator(0.1)],
        verbose_name="Total Acres (మొత్తం ఎకరాలు)",
        help_text="Total land area in acres"
    )
    
    sowing_date = models.DateField(
        verbose_name="Sowing Date (విత్తిన తేదీ)",
        help_text="Date when crop was sown"
    )
    
    # Storage & Financial Situation
    cold_storage = models.BooleanField(
        default=False,
        verbose_name="Cold Storage Access (కోల్డ్ స్టోరేజ్)",
        help_text="Do you have access to cold storage/warehouse?"
    )
    
    urgent_cash = models.BooleanField(
        default=False,
        verbose_name="Urgent Cash Need (తక్షణ నగదు అవసరం)",
        help_text="Do you need urgent cash from this crop?"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Farmer Record"
        verbose_name_plural = "Farmer Records"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.village} - {self.get_crop_display()} ({self.acres} acres)"
    
    def crop_age_days(self):
        """Calculate days since sowing"""
        return (timezone.now().date() - self.sowing_date).days


# ========================================
# Model 2: Disease Record (Crop Health)
# ========================================

class DiseaseRecord(models.Model):
    """
    Stores disease detection results for farmer's crop
    Linked to specific farmer submission
    """
    farmer = models.ForeignKey(
        Farmer,
        on_delete=models.CASCADE,
        related_name='diseases',
        verbose_name="Farmer"
    )
    
    disease_name = models.CharField(
        max_length=200,
        verbose_name="Disease Name (వ్యాధి పేరు)",
        help_text="Name of detected disease (e.g., Rice Blast, Mango Anthracnose)"
    )
    
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='low',
        verbose_name="Severity Level (తీవ్రత స్థాయి)",
        help_text="Disease severity impact on yield"
    )
    
    image = models.ImageField(
        upload_to='crop_images/%Y/%m/%d/',
        verbose_name="Crop Image",
        help_text="Upload photo of affected leaf/fruit"
    )
    
    yield_loss_percentage = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Yield Loss %",
        help_text="Estimated yield loss due to disease"
    )
    
    detection_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Detection Date"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Additional Notes"
    )
    
    class Meta:
        verbose_name = "Disease Record"
        verbose_name_plural = "Disease Records"
        ordering = ['-detection_date']
    
    def __str__(self):
        return f"{self.disease_name} - {self.get_severity_display()} ({self.farmer.crop})"


# ========================================
# Model 3: Weather Data (Environmental Factors)
# ========================================

class WeatherData(models.Model):
    """
    Stores weather data for each mandal
    Used to calculate weather impact on yield
    """
    mandal = models.CharField(
        max_length=50,
        choices=MANDAL_CHOICES,
        verbose_name="Mandal"
    )
    
    rainfall = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name="Rainfall (mm)",
        help_text="Rainfall in millimeters"
    )
    
    temperature = models.FloatField(
        verbose_name="Temperature (°C)",
        help_text="Average temperature in Celsius"
    )
    
    humidity = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Humidity (%)",
        help_text="Relative humidity percentage"
    )
    
    date = models.DateField(
        verbose_name="Date",
        help_text="Weather data date"
    )
    
    class Meta:
        verbose_name = "Weather Data"
        verbose_name_plural = "Weather Data"
        ordering = ['-date']
        unique_together = ['mandal', 'date']  # One record per mandal per day
    
    def __str__(self):
        return f"{self.get_mandal_display()} - {self.date} (Temp: {self.temperature}°C)"


# ========================================
# Model 4: Market Price (Mandi Prices)
# ========================================

class MarketPrice(models.Model):
    """
    Stores current and historical market prices for crops
    Used for profit calculation and selling recommendations
    """
    crop = models.CharField(
        max_length=50,
        choices=CROP_CHOICES,
        verbose_name="Crop"
    )
    
    region = models.CharField(
        max_length=100,
        verbose_name="Region/Mandi",
        help_text="Market location (e.g., Vijayawada, Guntur)"
    )
    
    price_per_quintal = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name="Price per Quintal (₹)",
        help_text="Current market price in Rupees per quintal"
    )
    
    date = models.DateField(
        verbose_name="Price Date",
        help_text="Date of price recording"
    )
    
    is_peak_season = models.BooleanField(
        default=False,
        verbose_name="Peak Season",
        help_text="Is this peak price season?"
    )
    
    class Meta:
        verbose_name = "Market Price"
        verbose_name_plural = "Market Prices"
        ordering = ['-date']
        unique_together = ['crop', 'region', 'date']  # One price per crop per region per day
    
    def __str__(self):
        return f"{self.get_crop_display()} - {self.region} - ₹{self.price_per_quintal}/Q ({self.date})"


# ========================================
# Model 5: Prediction Result (Final Output)
# ========================================

class PredictionResult(models.Model):
    """
    Stores the complete forecasting results for a farmer
    This is the final output combining all analyses
    """
    farmer = models.OneToOneField(
        Farmer,
        on_delete=models.CASCADE,
        related_name='prediction',
        verbose_name="Farmer"
    )
    
    # Yield Prediction
    predicted_yield = models.FloatField(
        verbose_name="Predicted Yield (Quintals)",
        help_text="Estimated total production in quintals"
    )
    
    yield_reduction_percentage = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Yield Reduction %",
        help_text="Percentage reduction due to disease & weather"
    )
    
    # Current Market Analysis
    current_market_price = models.FloatField(
        verbose_name="Current Market Price (₹/Q)",
        help_text="Current price per quintal"
    )
    
    total_current_value = models.FloatField(
        verbose_name="Total Current Value (₹)",
        help_text="Current total crop value (yield × current price)"
    )
    
    # Future Prediction
    predicted_peak_price = models.FloatField(
        verbose_name="Predicted Peak Price (₹/Q)",
        help_text="Expected peak price per quintal"
    )
    
    peak_price_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Peak Price Date",
        help_text="Expected date for peak price"
    )
    
    total_future_value = models.FloatField(
        verbose_name="Total Future Value (₹)",
        help_text="Potential crop value at peak price"
    )
    
    profit_delta = models.FloatField(
        verbose_name="Extra Profit by Waiting (₹)",
        help_text="Additional profit if waiting for peak price"
    )
    
    # Final Recommendation
    recommendation = models.CharField(
        max_length=20,
        choices=RECOMMENDATION_CHOICES,
        verbose_name="Final Recommendation",
        help_text="Store or Sell Now decision"
    )
    
    recommendation_reason = models.TextField(
        verbose_name="Recommendation Reason",
        help_text="Explanation for the recommendation"
    )
    
    confidence_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Confidence Score (%)",
        help_text="Prediction confidence level"
    )
    
    # Metadata
    generated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Generated At"
    )
    
    class Meta:
        verbose_name = "Prediction Result"
        verbose_name_plural = "Prediction Results"
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"Prediction for {self.farmer.village} - {self.farmer.get_crop_display()} ({self.get_recommendation_display()})"
    
    def profit_percentage(self):
        """Calculate profit increase percentage"""
        if self.total_current_value > 0:
            return round((self.profit_delta / self.total_current_value) * 100, 2)
        return 0
