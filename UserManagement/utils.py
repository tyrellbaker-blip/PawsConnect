from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.db import transaction
from django.db.models import Q

from PetManagement.models import Pet
from .models import CustomUser


@transaction.atomic
def create_user(cls, username, email, password, num_pets, pet_data):
    user = cls.objects.create_user(username=username, email=email, password=password)

    # Create pets
    for pet in pet_data:
        Pet.objects.create(owner=user, **pet)

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
    queryset = Pet.objects.all()
    if pet_id:
        queryset = queryset.filter(id=pet_id)
    if name:
        queryset = queryset.filter(name__icontains=name)
    return queryset
