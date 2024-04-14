from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import TestCase
from django.db import transaction

from PetManagement.models import Pet
from UserManagement.models import CustomUser

class PetAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        cls.another_user = CustomUser.objects.create_user(username='anotheruser', password='testpass')
        cls.pet = Pet.objects.create(name='Buddy', owner=cls.user, pet_type='Dog', age=3)
        cls.another_pet = Pet.objects.create(name='Another Pet', owner=cls.another_user, pet_type='Fish', age=1)

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        self.client.logout()

    @transaction.atomic
    def test_create_pet(self):
        url = reverse('PetManagement:pet-list')
        data = {'name': 'Max', 'pet_type': "Cat", 'age': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['pet_type'], 'Cat')

    @transaction.atomic
    def test_list_pets(self):
        url = reverse('PetManagement:pet-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    @transaction.atomic
    def test_retrieve_pet(self):
        url = reverse('PetManagement:pet-detail', args=[self.pet.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Buddy')

    @transaction.atomic
    def test_update_pet(self):
        url = reverse('PetManagement:pet-detail', args=[self.pet.id])
        data = {'name': 'Buddy Updated', 'age': 4}
        response = self.client.patch(url, data)
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.name, 'Buddy Updated')
        self.assertEqual(self.pet.age, 4)

    @transaction.atomic
    def test_delete_pet(self):
        url = reverse('PetManagement:pet-detail', args=[self.pet.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @transaction.atomic
    def test_create_pet_unauthorized(self):
        self.client.force_authenticate(user=None)
        url = reverse('PetManagement:pet-list')
        data = {'name': 'Unauthorized Pet', 'pet_type': 'Bird', 'age': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @transaction.atomic
    def test_update_pet_unauthorized(self):
        self.client.force_authenticate(user=self.another_user)
        url = reverse('PetManagement:pet-detail', args=[self.pet.id])
        data = {'name': 'Unauthorized Update'}
        response = self.client.patch(url, data)
        self.assertTrue(Pet.objects.filter(id=self.pet.id).exists())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @transaction.atomic
    def test_delete_pet_unauthorized(self):
        self.client.force_authenticate(user=self.another_user)
        url = reverse('PetManagement:pet-detail', args=[self.pet.id])
        response = self.client.delete(url)
        # Check if pet exists and if the status code matches expected unauthorized access
        self.assertTrue(Pet.objects.filter(id=self.pet.id).exists())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @transaction.atomic
    def test_list_pets_filtered_by_owner(self):
        url = reverse('PetManagement:pet-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Buddy')

    @transaction.atomic
    def test_retrieve_pet_unauthorized(self):
        self.client.force_authenticate(user=self.another_user)
        url = reverse('PetManagement:pet-detail', args=[self.pet.id])
        response = self.client.get(url)
        self.assertTrue(Pet.objects.filter(id=self.pet.id).exists())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @transaction.atomic
    def test_valid_transfer_request(self):
        data = {'pet': self.pet.id, 'to_user': self.another_user.username}
        url = reverse('PetManagement:pet-transfer-request-list')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
