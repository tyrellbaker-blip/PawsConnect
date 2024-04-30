import json

import requests
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db import transaction
from django.db.models import Q

from PawsConnect import settings
from PetManagement.models import Pet
from .models import CustomUser


@transaction.atomic
def create_user(cls, email, password, pets, **extra_fields):
    # Generate a username based on the first_name and last_name
    username = (extra_fields.get('first_name', '') + '_' + extra_fields.get('last_name', '')).lower()

    # Geocode the user's location
    city = extra_fields.get('city')
    state = extra_fields.get('state')
    zip_code = extra_fields.get('zip_code')

    if city and state and zip_code:
        address = f"{city}, {state}, {zip_code}"
        try:
            response = requests.get(
                f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={settings.GOOGLE_MAPS_API_KEY}"
            )
            response.raise_for_status()
            location = response.json()['results'][0]['geometry']['location']
            extra_fields['location'] = Point(location['lng'], location['lat'])
        except (requests.exceptions.RequestException, IndexError, KeyError):
            pass  # Handle geocoding failure gracefully

    user = cls.objects.create_user(username=username, email=email, password=password, **extra_fields)

    # Create pets
    if pets:
        pet_data = json.loads(pets)
        for pet in pet_data:
            Pet.objects.create(
                owner=user,
                name=pet.get('name', ''),
                pet_type=pet.get('pet_type', ''),
                age=pet.get('age', None),
                description=pet.get('description', '')
            )

    return user, user.slug


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
    queryset = Pet.objects.all()
    if pet_id:
        queryset = queryset.filter(id=pet_id)
    if name:
        queryset = queryset.filter(name__icontains=name)
    return queryset
