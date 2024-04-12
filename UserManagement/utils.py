from django.db import transaction
from PetManagement.forms import PetForm
from.models import set_profile_incomplete


# UserManagement/utils.py



@transaction.atomic
def create_user(cls, username, email, password, num_pets, pet_form_data):
    user = cls.objects.create_user(username=username, email=email, password=password)

    # Create pets
    for i in range(num_pets):
        pet_form = PetForm(pet_form_data[i], prefix=str(i))
        if pet_form.is_valid():
            pet = pet_form.save(commit=False)
            pet.owner = user
            pet.save()

    # Set profile completeness
    set_profile_incomplete(user)

    return user, True