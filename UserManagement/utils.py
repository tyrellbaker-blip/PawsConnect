from django.contrib.gis.measure import D, Distance
from elasticsearch_dsl import Q





def search_users(query=None, location_point=None, search_range=None):
    from UserManagement.models import CustomUser
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
    from PetManagement.models import Pet
    queryset = Pet.objects.all()
    if pet_id:
        queryset = queryset.filter(id=pet_id)
    if name:
        queryset = queryset.filter(name__icontains=name)
    return queryset
