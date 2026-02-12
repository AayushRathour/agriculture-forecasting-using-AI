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
    
    # User Auth URLs
    path('login/', views.user_login, name='user_login'),
    path('register/', views.user_register, name='user_register'),
    path('logout/', views.user_logout, name='user_logout'),
    path('profile/', views.user_profile, name='user_profile'),
    
    # Data Analytics
    path('data-analytics/', views.data_analytics, name='data_analytics'),
]
