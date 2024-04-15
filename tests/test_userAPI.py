from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from UserManagement.models import CustomUser
from PetManagement.models import Pet, PetTransferRequest

class PetTransferRequestAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sender = CustomUser.objects.create_user(username='sender', email='sender@example.com', password='testpass')
        cls.recipient = CustomUser.objects.create_user(username='recipient', email='recipient@example.com', password='testpass')
        cls.pet = Pet.objects.create(name='Buddy', owner=cls.sender, pet_type='Dog', age=3)

    def test_create_transfer_request(self):
        url = reverse('PetManagement:pet-transfer-request-list')
        self.client.force_authenticate(user=self.sender)
        data = {'pet': self.pet.id, 'to_user': self.recipient.username}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PetTransferRequest.objects.count(), 1)

    def test_list_transfer_requests(self):
        PetTransferRequest.objects.create(pet=self.pet, from_user=self.sender, to_user=self.recipient)
        url = reverse('PetManagement:pet-transfer-request-list')
        self.client.force_authenticate(user=self.sender)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_transfer_request(self):
        transfer_request = PetTransferRequest.objects.create(pet=self.pet, from_user=self.sender, to_user=self.recipient)
        url = reverse('PetManagement:pet-transfer-request-detail', args=[transfer_request.id])
        self.client.force_authenticate(user=self.sender)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], transfer_request.id)

    def test_accept_transfer_request(self):
        transfer_request = PetTransferRequest.objects.create(pet=self.pet, from_user=self.sender, to_user=self.recipient)
        url = reverse('PetManagement:pet-transfer-request-accept', args=[transfer_request.id])
        self.client.force_authenticate(user=self.recipient)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        transfer_request.refresh_from_db()
        self.assertEqual(transfer_request.status, PetTransferRequest.TransferStatus.APPROVED)
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.owner, self.recipient)

    def test_reject_transfer_request(self):
        transfer_request = PetTransferRequest.objects.create(pet=self.pet, from_user=self.sender, to_user=self.recipient)
        url = reverse('PetManagement:pet-transfer-request-reject', args=[transfer_request.id])
        self.client.force_authenticate(user=self.recipient)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        transfer_request.refresh_from_db()
        self.assertEqual(transfer_request.status, PetTransferRequest.TransferStatus.REJECTED)

    def test_unauthorized_accept_transfer_request(self):
        transfer_request = PetTransferRequest.objects.create(pet=self.pet, from_user=self.sender, to_user=self.recipient)
        url = reverse('PetManagement:pet-transfer-request-accept', args=[transfer_request.id])
        self.client.force_authenticate(user=self.sender)  # Sender trying to accept their own request
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_reject_transfer_request(self):
        transfer_request = PetTransferRequest.objects.create(pet=self.pet, from_user=self.sender, to_user=self.recipient)
        url = reverse('PetManagement:pet-transfer-request-reject', args=[transfer_request.id])
        self.client.force_authenticate(user=self.sender)  # Sender trying to reject their own request
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_accept_non_pending_transfer_request(self):
        transfer_request = PetTransferRequest.objects.create(pet=self.pet, from_user=self.sender, to_user=self.recipient, status=PetTransferRequest.TransferStatus.APPROVED)
        url = reverse('PetManagement:pet-transfer-request-accept', args=[transfer_request.id])
        self.client.force_authenticate(user=self.recipient)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_non_pending_transfer_request(self):
        transfer_request = PetTransferRequest.objects.create(pet=self.pet, from_user=self.sender, to_user=self.recipient, status=PetTransferRequest.TransferStatus.APPROVED)
        url = reverse('PetManagement:pet-transfer-request-reject', args=[transfer_request.id])
        self.client.force_authenticate(user=self.recipient)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_transfer_request_to_self(self):
        url = reverse('PetManagement:pet-transfer-request-list')
        self.client.force_authenticate(user=self.sender)
        data = {'pet': self.pet.id, 'to_user': self.sender.username}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)