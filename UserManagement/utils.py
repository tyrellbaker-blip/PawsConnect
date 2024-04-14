from django.db import transaction
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.db.models import Q

from PetManagement.forms import PetForm
from PetManagement.models import Pet  # Import for search_pets
from PetManagement.serializers import PetSerializer  # Import for search_pets
from .models import CustomUser
from .serializers import CustomUserSerializer  # Import for other functions

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
    user.set_profile_incomplete()

    return user, True

def search_users(query=None, location_point=None, search_range=None):
    queryset = CustomUser.objects.all()
    if query:
        queryset = queryset.filter(
            Q(username__icontains=query) | Q(display_name__icontains=query)
        )
    if location_point and search_range:
        search_distance = D(mi=search_range)
        queryset = queryset.annotate(
            distance=Distance('location', location_point)
        ).filter(distance__lte=search_distance)
    return queryset

def search_pets(pet_id=None, name=None):
    queryset = Pet.objects.all()  # Use imported Pet model
    if pet_id:
        queryset = queryset.filter(id=pet_id)
    if name:
        queryset = queryset.filter(name__icontains=name)
    return queryset