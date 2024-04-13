# PetManagement/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from PetManagement.models import Pet
from PetManagement.serializers import PetSerializer

class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)