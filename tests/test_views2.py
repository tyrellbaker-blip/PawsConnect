import unittest
from UserManagement import views
from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpRequest
from django.test import TestCase, RequestFactory
from unittest.mock import MagicMock, patch


class AddPetTest(TestCase):

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testUser', email='test@test.com', password='testpassword')

    def test_function_exists(self):
        self.assertIsNotNone(views.add_pet)

    def test_logged_out(self):
        request = self.factory.get('/add_pet')
        request.user = AnonymousUser()
        response = views.add_pet(request)
        # Expect a redirect 
        self.assertEqual(response.status_code, 302)

    @patch('UserManagement.views.PetForm')
    def test_add_pet(self, mock_form):
        request = self.factory.post('/add_pet')
        request.user = self.user

        # Assuming that the form is valid.
        mock_form.return_value.is_valid.return_value = True
        mock_form.return_value.save.return_value = MagicMock()

        response = views.add_pet(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'UserManagement:pets')

    @patch('UserManagement.views.PetForm')
    def test_invalid_form(self, mock_form):
        request = self.factory.post('/add_pet')
        request.user = self.user

        # Assuming that the form is not valid.
        mock_form.return_value.is_valid.return_value = False

        response = views.add_pet(request)
        self.assertEqual(response.status_code, 200)
