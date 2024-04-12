from django import forms
from django.forms import inlineformset_factory
from .models import Pet

class PetForm(forms.ModelForm):
    name = forms.CharField(label='Name', max_length=255, required=True)
    pet_type = forms.ChoiceField(label='Type', choices=Pet.PetType.choices, required=True)
    age = forms.IntegerField(label='Age', required=True)
    profile_picture = forms.ImageField(label='Profile Picture', required=False)
    description = forms.CharField(label='Description', widget=forms.Textarea, required=False)
    breed = forms.CharField(label='Breed', max_length=255, required=False)
    color = forms.CharField(label='Color', max_length=50, required=False)

    class Meta:
        model = Pet
        fields = ['name', 'pet_type', 'age', 'profile_picture', 'description', 'breed', 'color']

    def __init__(self, *args, **kwargs):
        super(PetForm, self).__init__(*args, **kwargs)
        self.fields['slug'].required = False

def get_pet_formset():
    from UserManagement.models import CustomUser  # Import here to avoid circular import
    return inlineformset_factory(
        CustomUser, Pet, form=PetForm,
        fields=['name', 'pet_type', 'age', 'profile_picture'], extra=1, can_delete=True
    )
