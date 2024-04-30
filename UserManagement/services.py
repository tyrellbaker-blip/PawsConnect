from django.contrib.auth import get_user_model

from PetManagement.models import Pet
from .geocoding import geocode_address
import json

User = get_user_model()

def create_user_with_pets(email, password, pets, **extra_fields):
    location = geocode_address(extra_fields.get('city'), extra_fields.get('state'), extra_fields.get('zip_code'))
    if location:
        extra_fields['location'] = location

    user = User.objects.create_user(email=email, password=password, **extra_fields)

    if pets:
        create_pets_for_user(user, pets)

    return user

def create_pets_for_user(user, pets_json):
    pets = json.loads(pets_json)
    for pet in pets:
        Pet.objects.create(owner=user, **pet)