from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from django.contrib.auth import authenticate
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


class UserRegistrationForm(UserCreationForm):
    preferred_language = forms.ChoiceField(choices=[
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('zh', 'Chinese (Mandarin)')
    ], widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'username', 'email', 'display_name', 'profile_picture', 'location', 'preferred_language', 'password1',
                  'password2']


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
