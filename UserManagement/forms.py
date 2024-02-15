from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username or Email", required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['username', 'password']


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'display_name', 'profile_picture', 'location', 'preferred_language', 'password1',
                  'password2']
