import logging

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
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
