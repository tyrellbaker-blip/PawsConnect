from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PetViewSet, PetTransferRequestViewSet, pet_profile_picture

router = DefaultRouter()
router.register(r'pets', PetViewSet, basename='pet')
router.register(r'pet-transfer-requests', PetTransferRequestViewSet, basename='pet-transfer-request')

app_name = 'PetManagement'

urlpatterns = [
    path('api/', include(router.urls)),
    path('pet/<slug:slug>/profile-picture/', pet_profile_picture, name='pet-profile-picture'),
    path('api/pets/search/', PetViewSet.as_view({'get': 'search'}), name='pet-search')
]
