from django import forms

from .models import Pet


class PetForm(forms.ModelForm):
    name = forms.CharField(label='Name', max_length=255, required=True)
    pet_type = forms.ChoiceField(label='Type', choices=Pet.PET_TYPE_CHOICES, required=True)
    age = forms.IntegerField(label='Age', required=True)
    profile_picture = forms.ImageField(label='Profile Picture', required=False)
    description = forms.CharField(label='Description', widget=forms.Textarea, required=False)
    breed = forms.CharField(label='Breed', max_length=255, required=False)
    color = forms.CharField(label='Color', max_length=50, required=False)

    class Meta:
        model = Pet
        fields = ['name', 'pet_type', 'age', 'profile_picture', 'description', 'breed', 'color']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False

