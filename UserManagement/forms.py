import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from django.contrib.auth import authenticate
from django.contrib.gis.geos import Point
from geopy import Nominatim
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut

from .models import CustomUser


class CustomLoginForm(forms.Form):
    username = forms.CharField(label="Username", required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if not authenticate(username=username, password=password):
            raise forms.ValidationError(
                "Invalid login details. Please, try again."
            )
        return cleaned_data


logger = logging.getLogger(__name__)


class UserRegistrationForm(UserCreationForm):
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=100, required=False)
    zip_code = forms.CharField(max_length=12, required=False)
    preferred_language = forms.ChoiceField(choices=[
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('zh', 'Chinese (Mandarin)')
    ], widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'username', 'email', 'city', 'state', 'zip_code', 'preferred_language',
                  'password1', 'password2']

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)

        # Attempt geocoding
        try:
            geolocator = Nominatim(user_agent="your_app_name")
            location_query = f"{self.cleaned_data.get('city')}, {self.cleaned_data.get('state')}, {self.cleaned_data.get('zip_code')}"
            location = geolocator.geocode(location_query, timeout=10)

            if location:
                user.location = Point(location.longitude, location.latitude)
            else:
                # Log if geocoding was unsuccessful (e.g., address not found)
                logger.warning(f"Geocoding failed for: {location_query}")
        except (GeocoderUnavailable, GeocoderTimedOut) as e:
            # Log the error and proceed without setting the location
            logger.error(f"Geocoding service error: {e}")

        if commit:
            user.save()

        return user


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'display_name', 'profile_picture', 'location', 'preferred_language']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'display_name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'preferred_language': forms.Select(choices=[
                ('en', 'English'),
                ('es', 'Spanish'),
                ('fr', 'French'),
                ('zh', 'Chinese (Mandarin)')
            ], attrs={'class': 'form-control'}),
        }
