from django.db import transaction
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .models import Pet, PetTransferRequest
from .permissions import IsOwnerPermission, IsOwnerOrRecipient
from .serializers import PetSerializer, PetTransferRequestSerializer


class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerPermission]

    @action(detail=False, methods=['get'])
    def search(self, request):
        from PetManagement.serializers import PetSearchSerializer
        pet_id = request.query_params.get('pet_id')
        pet_name = request.query_params.get('pet_name')

        queryset = Pet.objects.all()

        if pet_id:
            queryset = queryset.filter(id=pet_id)
        if pet_name:
            queryset = queryset.filter(name__icontains=pet_name)

        serializer = PetSearchSerializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """ Custom implementation to delete a pet only if certain conditions are met. """
        instance = self.get_object()
        if not request.user == instance.owner:
            return Response({"detail": "You do not have permission to delete this pet."},
                            status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        return Pet.objects.filter(owner=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class PetTransferRequestViewSet(viewsets.ModelViewSet):
    queryset = PetTransferRequest.objects.all()
    serializer_class = PetTransferRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrRecipient]

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        transfer_request = self.get_object()
        if transfer_request.to_user != request.user:
            return Response({'error': 'You are not authorized to accept this transfer request.'},
                            status=status.HTTP_403_FORBIDDEN)
        if transfer_request.status != PetTransferRequest.TransferStatus.PENDING:
            return Response({'error': 'Transfer request is not pending.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            pet = transfer_request.pet
            pet.owner = transfer_request.to_user
            pet.save()

            transfer_request.from_user.pets.remove(pet)
            transfer_request.to_user.pets.add(pet)

            transfer_request.status = PetTransferRequest.TransferStatus.APPROVED
            transfer_request.save()

        return Response({'message': 'Pet transfer successful.'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        transfer_request = self.get_object()
        if transfer_request.to_user != request.user:
            return Response({'error': 'You are not authorized to reject this transfer request.'},
                            status=status.HTTP_403_FORBIDDEN)
        if transfer_request.status != PetTransferRequest.TransferStatus.PENDING:
            return Response({'error': 'Transfer request is not pending.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            transfer_request.status = PetTransferRequest.TransferStatus.REJECTED
            transfer_request.save()

        return Response({'message': 'Pet transfer rejected.'})


from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Pet


def pet_profile_picture(request, slug):
    pet = get_object_or_404(Pet, slug=slug)
    if pet.profile_picture:
        return HttpResponse(pet.profile_picture, content_type='image/jpeg')
    else:
        # Return a default image or a 404 response
        return HttpResponse('No profile picture found.', status=404)
