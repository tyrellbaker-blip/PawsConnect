import logging
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from PetManagement.models import Pet
from .models import CustomUser


class CustomLoginForm(forms.Form):
    username = forms.CharField(label="Username", required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        try:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Invalid username or password.")
        except CustomUser.DoesNotExist:
            raise forms.ValidationError("User with that username does not exist.")

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
            user.save()  # This will trigger the geocoding logic in the model

        return user

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        # This should remove the help_text for password1.
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['username'].help_text = None

    def clean_username(self):
        username = self.cleaned_data["username"]

        try:
            CustomUser.objects.get(username=username)
            raise forms.ValidationError("A user with that username already exists.")
        except CustomUser.DoesNotExist:
            return username

    def clean_email(self):
        email = self.cleaned_data["email"]

        try:
            CustomUser.objects.get(email=email)
            raise forms.ValidationError("A user with that email address already exists.")
        except CustomUser.DoesNotExist:
            return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match.")

        # Add your password complexity and length checks here
        if password1:
            if len(password1) < 8:
                raise ValidationError("Password must be at least 8 characters long.")
            if not any(char.isdigit() for char in password1):
                raise ValidationError("Password must contain at least one digit.")
            if not any(char.isupper() for char in password1):
                raise ValidationError("Password must contain at least one uppercase letter.")
            if not any(char.islower() for char in password1):
                raise ValidationError("Password must contain at least one lowercase letter.")
            if not any(char in "!@#$%^&*()" for char in password1):
                raise ValidationError("Password must contain at least one special character: !@#$%^&*().")

        return password2


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


class UserCompletionForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['display_name', 'city', 'state', 'zip_code',
                  'preferred_language', 'profile_picture', 'has_pets', 'about_me']


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
    range = forms.ChoiceField(choices=DISTANCE_CHOICES, required=False, label='Range',
                              help_text='Select search radius for location-based search.')
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
        if search_type == 'user' and any(
                [cleaned_data.get('city'), cleaned_data.get('state'), cleaned_data.get('zip_code')]) and not all(
                [cleaned_data.get('city'), cleaned_data.get('state'), cleaned_data.get('zip_code')]):
            raise ValidationError("Please provide a complete address: city, state, and zip code for location-based "
                                  "searches.")

        return cleaned_data
