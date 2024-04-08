import logging
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import GoogleV3


from PetManagement.models import Pet
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
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    has_pets = forms.ChoiceField(choices=[(True, 'Yes'), (False, 'No')], widget=forms.RadioSelect,
                                 label='Do you have pets?')

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ['username', 'display_name', 'first_name', 'last_name', 'email', 'password1', 'password2', 'city',
                  'state', 'zip_code',
                  'preferred_language', 'profile_picture', 'has_pets', 'about_me']

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()

        return user

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        # This should remove the help_text for password1.
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['username'].help_text = None


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'display_name', 'profile_picture', 'location',
                  'preferred_language']
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


class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['name', 'pet_type', 'age', 'profile_picture']


PetFormSet = inlineformset_factory(
    CustomUser, Pet, form=PetForm,
    fields=['name', 'pet_type', 'age', 'profile_picture'], extra=1, can_delete=True
)


class SearchForm(forms.Form):
    QUERY_CHOICES = [
        ('user', 'User'),
        ('pet', 'Pet'),
    ]
    DISTANCE_CHOICES = [
        ('5', '5 miles'),
        ('10', '10 miles'),
        ('20', '20 miles'),
        ('50', '50+ miles'),
    ]

    query = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Username or Pet Name...'}))
    type = forms.ChoiceField(choices=QUERY_CHOICES, widget=forms.RadioSelect, initial='user')
    # Location fields for 'user' type search
    city = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'City'}))
    state = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'State'}))
    zip_code = forms.CharField(max_length=12, required=False, widget=forms.TextInput(attrs={'placeholder': 'Zip Code'}))
    # Distance choice for 'location' type search under 'user'
    range = forms.ChoiceField(choices=DISTANCE_CHOICES, required=False, label='Range', help_text='Select search radius for location-based search.')
    # Fields for 'pet' type search
    pet_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Pet ID'}))
    pet_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Pet Name'}))

    def clean(self):
        cleaned_data = super().clean()
        search_type = cleaned_data.get('type')
        query = cleaned_data.get('query')
        pet_id = cleaned_data.get('pet_id')
        pet_name = cleaned_data.get('pet_name')

        # Check for at least one search criterion based on the search type
        if search_type == 'user':
            if not any([query, cleaned_data.get('city')]):
                raise ValidationError('Please specify a username or location for user search.')
        elif search_type == 'pet':
            if not any([pet_id, pet_name]):
                raise ValidationError('Please specify a pet ID or pet name for pet search.')

        # Additional location validation for 'user' type search
        if search_type == 'user' and any([cleaned_data.get('city'), cleaned_data.get('state'), cleaned_data.get('zip_code')]) and not all([cleaned_data.get('city'), cleaned_data.get('state'), cleaned_data.get('zip_code')]):
            raise ValidationError("Please provide a complete address: city, state, and zip code for location-based searches.")

        # Handle geolocation for 'user' type search if location fields are filled
        if search_type == 'user' and all([cleaned_data.get('city'), cleaned_data.get('state'), cleaned_data.get('zip_code')]):
            self._geocode_location(cleaned_data)

        return cleaned_data

    def _geocode_location(self, cleaned_data):
        city = cleaned_data.get('city')
        state = cleaned_data.get('state')
        zip_code = cleaned_data.get('zip_code')

        geolocator = GoogleV3(api_key=settings.GOOGLE_MAPS_API_KEY)
        try:
            location_query = f"{city}, {state}, {zip_code}"
            location = geolocator.geocode(location_query, timeout=10)
            if location:
                cleaned_data['location_point'] = Point(location.longitude, location.latitude, srid=4326)
            else:
                self.add_error('city', "Geocoding failed for the provided address.")
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            self.add_error('city', f"Geocoding service error: {e}")
