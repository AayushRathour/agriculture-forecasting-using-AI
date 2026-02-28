"""
Forms for the forecast app
Provides form validation and processing for user inputs
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Farmer, DiseaseRecord, WeatherData, MarketPrice


class FarmerInputForm(forms.ModelForm):
    """Form for farmer crop data input"""
    
    class Meta:
        model = Farmer
        fields = ['mandal', 'village', 'crop', 'acres', 'sowing_date', 
                  'cold_storage', 'urgent_cash']
        widgets = {
            'mandal': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'village': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your village name',
                'required': True
            }),
            'crop': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'acres': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter land area in acres',
                'min': '0.1',
                'step': '0.1',
                'required': True
            }),
            'sowing_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'cold_storage': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'urgent_cash': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean_acres(self):
        """Validate acres field"""
        acres = self.cleaned_data.get('acres')
        if acres and acres <= 0:
            raise forms.ValidationError('Acres must be greater than 0')
        if acres and acres > 1000:
            raise forms.ValidationError('Acres seems too large. Please verify.')
        return acres


class DiseaseRecordForm(forms.ModelForm):
    """Form for disease detection data"""
    
    class Meta:
        model = DiseaseRecord
        fields = ['disease_name', 'severity', 'image', 'notes']
        widgets = {
            'disease_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter disease name (optional)'
            }),
            'severity': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'required': True
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes (optional)'
            }),
        }
    
    def clean_image(self):
        """Validate image file"""
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image file size must be less than 5MB')
            
            # Check file extension
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
            ext = image.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    f'Invalid file type. Please upload: {", ".join(valid_extensions)}'
                )
        return image


class CustomUserRegistrationForm(UserCreationForm):
    """Enhanced user registration form with email"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    
    first_name = forms.CharField(
        required=False,
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name (optional)'
        })
    )
    
    last_name = forms.CharField(
        required=False,
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name (optional)'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    
    def clean_email(self):
        """Validate unique email"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered')
        return email


class WeatherDataForm(forms.ModelForm):
    """Form for adding weather data (admin use)"""
    
    class Meta:
        model = WeatherData
        fields = ['mandal', 'rainfall', 'temperature', 'humidity', 'date']
        widgets = {
            'mandal': forms.Select(attrs={'class': 'form-control'}),
            'rainfall': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0'
            }),
            'temperature': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1'
            }),
            'humidity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class MarketPriceForm(forms.ModelForm):
    """Form for adding market prices (admin use)"""
    
    class Meta:
        model = MarketPrice
        fields = ['crop', 'region', 'price_per_quintal', 'date', 'is_peak_season']
        widgets = {
            'crop': forms.Select(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Market/Mandi name'
            }),
            'price_per_quintal': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_peak_season': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
