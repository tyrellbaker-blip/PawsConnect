from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PetViewSet, PetTransferRequestViewSet

router = DefaultRouter()
router.register(r'pets', PetViewSet, basename='pet')
router.register(r'pet-transfer-requests', PetTransferRequestViewSet, basename='pet-transfer-request')

app_name = 'PetManagement'

urlpatterns = [
    path('', include(router.urls)),
]