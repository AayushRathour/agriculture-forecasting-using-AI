"""
URL patterns for the forecast app
"""

from django.urls import path
from . import views

app_name = 'forecast'

urlpatterns = [
    path('', views.home, name='home'),
    path('input/', views.input_form, name='input_form'),
    path('farmer-input/', views.farmer_input, name='farmer_input'),
    path('result/', views.result, name='result'),
    path('farmer/<int:farmer_id>/', views.farmer_detail, name='farmer_detail'),
    
    # Admin URLs
    path('af-admin/', views.admin_dashboard, name='admin_dashboard'),
    path('af-admin/login/', views.admin_login, name='admin_login'),
    path('af-admin/register/', views.admin_register, name='admin_register'),
    
    # Admin Management URLs
    path('af-admin/users/', views.admin_users, name='admin_users'),
    path('af-admin/users/create/', views.admin_user_create, name='admin_user_create'),
    path('af-admin/users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('af-admin/users/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),
    
    path('af-admin/farmers/', views.admin_farmers, name='admin_farmers'),
    path('af-admin/farmers/<int:farmer_id>/', views.admin_farmer_detail, name='admin_farmer_detail'),
    path('af-admin/farmers/<int:farmer_id>/edit/', views.admin_farmer_edit, name='admin_farmer_edit'),
    path('af-admin/farmers/<int:farmer_id>/delete/', views.admin_farmer_delete, name='admin_farmer_delete'),
    path('af-admin/farmers/bulk-delete/', views.admin_farmers_bulk_delete, name='admin_farmers_bulk_delete'),
    
    path('af-admin/weather/', views.admin_weather, name='admin_weather'),
    path('af-admin/weather/add/', views.admin_weather_add, name='admin_weather_add'),
    path('af-admin/weather/<int:weather_id>/delete/', views.admin_weather_delete, name='admin_weather_delete'),
    
    path('af-admin/prices/', views.admin_prices, name='admin_prices'),
    path('af-admin/prices/add/', views.admin_price_add, name='admin_price_add'),
    path('af-admin/prices/<int:price_id>/delete/', views.admin_price_delete, name='admin_price_delete'),
    
    path('af-admin/export/farmers/', views.admin_export_farmers, name='admin_export_farmers'),
    path('af-admin/export/weather/', views.admin_export_weather, name='admin_export_weather'),
    path('af-admin/export/prices/', views.admin_export_prices, name='admin_export_prices'),
    
    path('af-admin/logs/', views.admin_logs, name='admin_logs'),
    path('af-admin/settings/', views.admin_settings, name='admin_settings'),
    path('af-admin/notifications/create/', views.admin_create_notification, name='admin_create_notification'),
    
    # User Auth URLs
    path('login/', views.user_login, name='user_login'),
    path('register/', views.user_register, name='user_register'),
    path('logout/', views.user_logout, name='user_logout'),
    path('profile/', views.user_profile, name='user_profile'),
    
    # Enhanced User Features
    path('crop-comparison/', views.crop_comparison, name='crop_comparison'),
    path('historical-analysis/', views.historical_analysis, name='historical_analysis'),
    path('export/<str:format>/', views.export_data, name='export_data'),
    path('price-alerts/', views.price_alerts, name='price_alerts'),
    path('price-alerts/<int:alert_id>/delete/', views.delete_alert, name='delete_alert'),
    path('favorites/toggle/<str:crop>/', views.toggle_favorite, name='toggle_favorite'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('recommendations/', views.crop_recommendations, name='crop_recommendations'),
    
    # Data Analytics
    path('data-analytics/', views.data_analytics, name='data_analytics'),
]
