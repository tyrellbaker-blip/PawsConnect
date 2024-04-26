import logging

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from rest_framework import serializers

from PetManagement.forms import PetForm
from PetManagement.models import Pet
from .models import CustomUser

PetFormSet = inlineformset_factory(
    CustomUser, Pet, form=PetForm,
    fields=['name', 'pet_type', 'age', 'profile_picture'], extra=1, can_delete=True
)



class CustomLoginForm(forms.Form):
    username = forms.CharField(label="Username", required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username or password.")
        return cleaned_data

    @classmethod
    def get_serializer(cls):
        class CustomLoginSerializer(serializers.Serializer):
            username = serializers.CharField(required=True)
            password = serializers.CharField(required=True)

        return CustomLoginSerializer


logger = logging.getLogger(__name__)


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    city = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=100, required=True)
    zip_code = forms.CharField(max_length=12, required=True)

    class Meta:
        model = CustomUser
        fields = [
            'username', 'display_name', 'first_name', 'last_name', 'email',
            'password1', 'password2', 'city', 'state', 'zip_code', 'preferred_language',
            'profile_picture'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.city = self.cleaned_data['city']
        user.state = self.cleaned_data['state']
        user.zip_code = self.cleaned_data['zip_code']
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        for field_name in ['password1', 'password2', 'username']:
            self.fields[field_name].help_text = None

    def clean_username(self):
        username = self.cleaned_data["username"]
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email address already exists.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match.")
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
    about_me = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = CustomUser
        exclude = ['location', 'password', 'last_login', 'is_superuser', 'username',
                   'is_staff', 'is_active', 'date_joined', 'groups', 'user_permissions',
                   'has_pets', 'profile_incomplete', 'slug', 'num_friends', 'pets']

        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'display_name': forms.TextInput(attrs={'class': 'form-control'}),
            'preferred_language': forms.Select(choices=[
                ('en', 'English'), ('es', 'Spanish'), ('fr', 'French'), ('zh', 'Chinese (Mandarin)')
            ], attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['city'].required = True
        self.fields['state'].required = True
        self.fields['zip_code'].required = True
        self.fields['about_me'].initial = self.instance.profile.about_me

    def save(self, commit=True):
        user = super().save(commit=False)
        user.profile.about_me = self.cleaned_data['about_me']
        if commit:
            user.save()
            user.profile.save()
        return user


class PetEditForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = '__all__'  # Include all fields from the Pet model
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'pet_type': forms.Select(choices=Pet.PetType.choices, attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'breed': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control-file'}),  # File input for image
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(PetEditForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['age'].required = True
        self.fields['color'].required = True
        self.fields['breed'].required = True
        self.fields['profile_picture'].required = False
        self.fields['description'].initial = self.instance.profile.description


class UserCompletionForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['display_name', 'city', 'state', 'zip_code', 'preferred_language', 'profile_picture', 'has_pets']

    def __init__(self, *args, **kwargs):
        super(UserCompletionForm, self).__init__(*args, **kwargs)
        self.fields['about_me'].initial = self.instance.profile.about_me

    def save(self, commit=True):
        user = super().save(commit=False)
        user.profile.about_me = self.cleaned_data['about_me']
        user.profile_incomplete = False
        if commit:
            user.save()
            user.profile.save()
        return user


class SearchForm(forms.Form):
    QUERY_CHOICES = [
        ('user', 'User'),
        ('pet', 'Pet'),
    ]
    DISTANCE_CHOICES = [
        (5, '5 miles'),
        (10, '10 miles'),
        (20, '20 miles'),
        (50, '50+ miles'),
    ]
    query = forms.CharField(required=False)
    type = forms.ChoiceField(choices=QUERY_CHOICES)
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=100, required=False)
    zip_code = forms.CharField(max_length=12, required=False)
    range = forms.ChoiceField(choices=DISTANCE_CHOICES, required=False)

    def clean(self):
        cleaned_data = super().clean()
        search_type = cleaned_data.get('type')
        city = cleaned_data.get('city')
        state = cleaned_data.get('state')
        zip_code = cleaned_data.get('zip_code')

        if search_type == 'user' and any([city, state, zip_code]) and not all([city, state, zip_code]):
            raise ValidationError(
                "Please provide a complete address: city, state, and zip code for location-based searches."
            )

        return cleaned_data
