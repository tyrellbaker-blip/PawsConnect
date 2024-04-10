from django.http import JsonResponse
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
import json

from PawsConnect import settings

User = get_user_model()

class UserRegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('UserManagement:register')

    def test_user_registration_with_valid_data(self):
        response = self.client.post(self.register_url, {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'city': 'New York',
            'state': 'NY',
            'zip_code': '10001',
            'preferred_language': 'en',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_user_registration_with_invalid_data(self):
        response = self.client.post(self.register_url, {
            'username': '',
            'email': 'invalid_email',
            'password1': 'testpassword',
            'password2': 'mismatchedpassword',
            'city': '',
            'state': '',
            'zip_code': '',
            'preferred_language': 'en',
        })
        self.assertEqual(response.status_code, 200)  # No redirect, render the registration form with errors
        self.assertFalse(User.objects.filter(username='testuser').exists())

    @patch('requests.get')
    def test_user_registration_with_valid_location(self, mock_get):
        mock_response = {
            'results': [
                {
                    'geometry': {
                        'location': {
                            'lat': 40.7128,
                            'lng': -74.0060
                        }
                    }
                }
            ]
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        response = self.client.post(self.register_url, {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'city': 'New York',
            'state': 'NY',
            'zip_code': '10001',
            'preferred_language': 'en',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        user = User.objects.get(username='testuser')
        self.assertEqual(user.latitude, 40.7128)
        self.assertEqual(user.longitude, -74.0060)

    @patch('requests.get')
    def test_user_registration_with_invalid_location(self, mock_get):
        mock_response = {
            'results': []
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        response = self.client.post(self.register_url, {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'city': 'InvalidCity',
            'state': 'InvalidState',
            'zip_code': '12345',
            'preferred_language': 'en',
        })
        self.assertEqual(response.status_code, 200)  # No redirect, render the registration form with errors
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_google_maps(request):
        api_key = settings.GOOGLE_MAPS_API_KEY
        response_data = {
            'google_maps_api_key': bool(api_key),
            }
        return JsonResponse(response_data)