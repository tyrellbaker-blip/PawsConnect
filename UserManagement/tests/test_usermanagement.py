import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from UserManagement.models import CustomUser

class UserRegistrationTestCase(APITestCase):
    def test_user_registration(self):
        url = reverse('UserManagement:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword',
            'first_name': 'New',
            'last_name': 'User',
            'display_name': 'New User',
            'about_me': 'I am a new user',
            'preferred_language': 'en',
            'city': 'New York',
            'state': 'NY',
            'zip_code': '10001',
            'has_pets': True,
            'pet_name': 'Buddy',
            'pet_age': 3,
            'pet_type': 'Dog',
            'pet_description': 'A friendly dog'
        }
        response = self.client.post(url, data, format='json')
        content = json.loads(response.content)
        self.assertIn('slug', content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertNotIn('id', response.data)
        self.assertIn('username', response.data)
        self.assertIn('slug', response.data)
        self.assertNotIn('profile_visibility', response.data)
        self.assertNotIn('location', response.data)
        self.assertIn('has_completed_profile', response.data)
        self.assertNotIn('num_friends', response.data)
        self.assertNotIn('friends', response.data)

        user = CustomUser.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.display_name, 'New User')
        self.assertEqual(user.about_me, 'I am a new user')
        self.assertEqual(user.preferred_language, 'en')
        self.assertEqual(user.city, 'New York')
        self.assertEqual(user.state, 'NY')
        self.assertEqual(user.zip_code, '10001')
        self.assertTrue(user.has_pets)
        self.assertEqual(user.pets.count(), 1)
        pet = user.pets.first()
        self.assertEqual(pet.name, 'Buddy')
        self.assertEqual(pet.age, 3)
        self.assertEqual(pet.pet_type, 'Dog')
        self.assertEqual(pet.description, 'A friendly dog')