from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from UserManagement.models import CustomUser


class AuthAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword123')
        self.login_url = reverse('login')
        self.profile_url = reverse('UserManagement:profile', kwargs={'slug': self.user.slug})

    def test_login(self):
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpassword123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)

    def test_user_profile_unauthorized(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_profile_authorized(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
