import unittest
from unittest.mock import Mock
from django.test import RequestFactory
from UserManagement.views import user_login


class TestUserLogin(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    # Case: Successful login with complete profile
    def test_successful_login_complete_profile(self):
        # Mocking POST request 
        request = self.factory.post('/login', {'username': 'test', 'password': '123'})
        request.method = 'POST'
        request.session = dict()
        request.user = Mock(username='test', password='123')
        request.user.is_profile_complete = True

        response = user_login(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/UserManagement/profile/test')

    # Case: Successful login with incomplete profile
    def test_successful_login_incomplete_profile(self):
        request = self.factory.post('/login', {'username': 'incomplete', 'password': '123'})
        request.method = 'POST'
        request.session = dict()
        request.user = Mock(username='incomplete', password='123')
        request.user.is_profile_complete = False

        response = user_login(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/UserManagement/user_completion')

    # Case: Invalid username or password 
    def test_invalid_login(self):
        request = self.factory.post('/login', {'username': 'invalid', 'password': '123'})
        request.method = 'POST'
        request.session = dict()
        request.user = Mock()
        request.user.is_profile_complete = False

        response = user_login(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid username or password", response.content)

    # Case: User does not exist
    def test_non_existent_user(self):
        request = self.factory.post('/login', {'username': 'nonexistent', 'password': '123'})
        request.method = 'POST'
        request.session = dict()
        request.user = None

        response = user_login(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"User with that username does not exist", response.content)


if __name__ == '__main__':
    unittest.main()
