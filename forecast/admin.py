"""
Admin panel configuration for the Crop Forecasting System
Customizes how models appear in Django admin interface
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Farmer, DiseaseRecord, WeatherData, MarketPrice, PredictionResult,
    PriceAlert, FavoriteCrop, Notification
)


# ========================================
# Farmer Admin
# ========================================

@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    """Admin interface for Farmer model"""
    
    list_display = [
        'id', 
        'village', 
        'mandal', 
        'crop', 
        'acres', 
        'sowing_date',
        'cold_storage_icon',
        'urgent_cash_icon',
        'created_at'
    ]
    
    list_filter = ['mandal', 'crop', 'cold_storage', 'urgent_cash', 'created_at']
    
    search_fields = ['village', 'mandal', 'crop']
    
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Location Information', {
            'fields': ('mandal', 'village')
        }),
        ('Crop Details', {
            'fields': ('crop', 'acres', 'sowing_date')
        }),
        ('Storage & Financial', {
            'fields': ('cold_storage', 'urgent_cash')
        }),
    )
    
    def cold_storage_icon(self, obj):
        """Display icon for cold storage availability"""
        if obj.cold_storage:
            return format_html('<span style="color: green;">✓ Yes</span>')
        return format_html('<span style="color: red;">✗ No</span>')
    cold_storage_icon.short_description = 'Cold Storage'
    
    def urgent_cash_icon(self, obj):
        """Display icon for urgent cash need"""
        if obj.urgent_cash:
            return format_html('<span style="color: orange;">⚠ Urgent</span>')
        return format_html('<span style="color: green;">✓ Normal</span>')
    urgent_cash_icon.short_description = 'Cash Need'


# ========================================
# Disease Record Admin
# ========================================

@admin.register(DiseaseRecord)
class DiseaseRecordAdmin(admin.ModelAdmin):
    """Admin interface for Disease Record model"""
    
    list_display = [
        'id',
        'farmer',
        'disease_name',
        'severity_badge',
        'yield_loss_percentage',
        'detection_date',
        'image_preview'
    ]
    
    list_filter = ['severity', 'detection_date', 'farmer__crop']
    
    search_fields = ['disease_name', 'farmer__village', 'notes']
    
    date_hierarchy = 'detection_date'
    
    readonly_fields = ['detection_date', 'image_preview']
    
    fieldsets = (
        ('Farmer Information', {
            'fields': ('farmer',)
        }),
        ('Disease Details', {
            'fields': ('disease_name', 'severity', 'yield_loss_percentage', 'notes')
        }),
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
        ('Metadata', {
            'fields': ('detection_date',)
        }),
    )
    
    def severity_badge(self, obj):
        """Display colored badge for severity"""
        colors = {
            'low': 'green',
            'medium': 'orange',
            'high': 'red'
        }
        color = colors.get(obj.severity, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_severity_display()
        )
    severity_badge.short_description = 'Severity'
    
    def image_preview(self, obj):
        """Display thumbnail of uploaded image"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 200px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Image Preview'


# ========================================
# Weather Data Admin
# ========================================

@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    """Admin interface for Weather Data model"""
    
    list_display = [
        'id',
        'mandal',
        'date',
        'temperature_display',
        'rainfall_display',
        'humidity_display'
    ]
    
    list_filter = ['mandal', 'date']
    
    search_fields = ['mandal']
    
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Location & Date', {
            'fields': ('mandal', 'date')
        }),
        ('Weather Parameters', {
            'fields': ('temperature', 'rainfall', 'humidity')
        }),
    )
    
    def temperature_display(self, obj):
        """Format temperature with unit"""
        return f"{obj.temperature}°C"
    temperature_display.short_description = 'Temperature'
    
    def rainfall_display(self, obj):
        """Format rainfall with unit"""
        return f"{obj.rainfall} mm"
    rainfall_display.short_description = 'Rainfall'
    
    def humidity_display(self, obj):
        """Format humidity with unit"""
        return f"{obj.humidity}%"
    humidity_display.short_description = 'Humidity'


# ========================================
# Market Price Admin
# ========================================

@admin.register(MarketPrice)
class MarketPriceAdmin(admin.ModelAdmin):
    """Admin interface for Market Price model"""
    
    list_display = [
        'id',
        'crop',
        'region',
        'price_display',
        'date',
        'peak_season_icon'
    ]
    
    list_filter = ['crop', 'region', 'is_peak_season', 'date']
    
    search_fields = ['crop', 'region']
    
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Crop & Location', {
            'fields': ('crop', 'region')
        }),
        ('Price Information', {
            'fields': ('price_per_quintal', 'date', 'is_peak_season')
        }),
    )
    
    def price_display(self, obj):
        """Format price with currency"""
        return format_html(
            '<strong style="color: green;">₹{:,.2f}/Q</strong>',
            obj.price_per_quintal
        )
    price_display.short_description = 'Price per Quintal'
    
    def peak_season_icon(self, obj):
        """Display icon for peak season"""
        if obj.is_peak_season:
            return format_html('<span style="color: gold;">⭐ Peak</span>')
        return format_html('<span style="color: gray;">Regular</span>')
    peak_season_icon.short_description = 'Season'


# ========================================
# Prediction Result Admin
# ========================================

@admin.register(PredictionResult)
class PredictionResultAdmin(admin.ModelAdmin):
    """Admin interface for Prediction Result model"""
    
    list_display = [
        'id',
        'farmer',
        'predicted_yield',
        'recommendation_badge',
        'profit_delta_display',
        'confidence_score',
        'generated_at'
    ]
    
    list_filter = ['recommendation', 'generated_at']
    
    search_fields = ['farmer__village', 'farmer__crop']
    
    date_hierarchy = 'generated_at'
    
    readonly_fields = ['generated_at', 'profit_percentage_display']
    
    fieldsets = (
        ('Farmer', {
            'fields': ('farmer',)
        }),
        ('Yield Prediction', {
            'fields': ('predicted_yield', 'yield_reduction_percentage')
        }),
        ('Current Market', {
            'fields': ('current_market_price', 'total_current_value')
        }),
        ('Future Prediction', {
            'fields': ('predicted_peak_price', 'peak_price_date', 'total_future_value')
        }),
        ('Profit Analysis', {
            'fields': ('profit_delta', 'profit_percentage_display')
        }),
        ('Recommendation', {
            'fields': ('recommendation', 'recommendation_reason', 'confidence_score')
        }),
        ('Metadata', {
            'fields': ('generated_at',)
        }),
    )
    
    def recommendation_badge(self, obj):
        """Display colored badge for recommendation"""
        if obj.recommendation == 'store':
            return format_html(
                '<span style="background-color: green; color: white; padding: 5px 15px; border-radius: 5px; font-weight: bold;">🟢 STORE</span>'
            )
        else:
            return format_html(
                '<span style="background-color: orange; color: white; padding: 5px 15px; border-radius: 5px; font-weight: bold;">🔴 SELL NOW</span>'
            )
    recommendation_badge.short_description = 'Recommendation'
    
    def profit_delta_display(self, obj):
        """Format profit delta with currency"""
        if obj.profit_delta > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">+₹{:,.2f}</span>',
                obj.profit_delta
            )
        return format_html(
            '<span style="color: red;">₹{:,.2f}</span>',
            obj.profit_delta
        )
    profit_delta_display.short_description = 'Extra Profit'
    
    def profit_percentage_display(self, obj):
        """Display profit percentage"""
        percentage = obj.profit_percentage()
        return format_html(
            '<span style="color: green; font-weight: bold;">+{}%</span>',
            percentage
        )
    profit_percentage_display.short_description = 'Profit Increase %'


# ========================================
# Price Alert Admin
# ========================================

@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    """Admin interface for Price Alert model"""
    
    list_display = [
        'id',
        'user',
        'crop',
        'target_price',
        'status_badge',
        'created_at',
        'triggered_at'
    ]
    
    list_filter = ['crop', 'is_active', 'is_triggered', 'created_at']
    
    search_fields = ['user__username', 'crop']
    
    date_hierarchy = 'created_at'
    
    def status_badge(self, obj):
        """Display status with color coding"""
        if obj.is_triggered:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 10px; border-radius: 3px;">✓ Triggered</span>'
            )
        elif obj.is_active:
            return format_html(
                '<span style="background-color: blue; color: white; padding: 3px 10px; border-radius: 3px;">● Active</span>'
            )
        else:
            return format_html(
                '<span style="background-color: gray; color: white; padding: 3px 10px; border-radius: 3px;">○ Inactive</span>'
            )
    status_badge.short_description = 'Status'


# ========================================
# Favorite Crop Admin
# ========================================

@admin.register(FavoriteCrop)
class FavoriteCropAdmin(admin.ModelAdmin):
    """Admin interface for Favorite Crop model"""
    
    list_display = ['id', 'user', 'crop', 'added_at']
    
    list_filter = ['crop', 'added_at']
    
    search_fields = ['user__username', 'crop']
    
    date_hierarchy = 'added_at'


# ========================================
# Notification Admin
# ========================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model"""
    
    list_display = [
        'id',
        'user',
        'notification_type',
        'title',
        'read_badge',
        'created_at',
        'read_at'
    ]
    
    list_filter = ['notification_type', 'is_read', 'created_at']
    
    search_fields = ['user__username', 'title', 'message']
    
    date_hierarchy = 'created_at'
    
    readonly_fields = ['created_at', 'read_at']
    
    def read_badge(self, obj):
        """Display read status with color coding"""
        if obj.is_read:
            return format_html(
                '<span style="background-color: gray; color: white; padding: 3px 10px; border-radius: 3px;">✓ Read</span>'
            )
        else:
            return format_html(
                '<span style="background-color: orange; color: white; padding: 3px 10px; border-radius: 3px;">● Unread</span>'
            )
    read_badge.short_description = 'Status'

