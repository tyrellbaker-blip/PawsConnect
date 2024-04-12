from django.test import TestCase

from UserManagement.forms import SearchForm


class SearchFormTest(TestCase):
    def test_valid_data_user_search(self):
        form_data = {
            'type': 'user',
            'query': 'john',
            'city': 'San Francisco',
            'state': 'CA',
            'zip_code': '94103',
            'range': '10',
        }
        form = SearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_data_missing_location_fields(self):
        form_data = {
            'type': 'user',
            'city': 'Some City',
        }
        form = SearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Please provide a complete address: city, state, and zip code for location-based searches.',
                      form.errors['__all__'])

    def test_missing_required_fields(self):
        form_data = {
            'city': 'San Francisco',
            'range': '10',
        }
        form = SearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('type', form.errors)


from unittest.mock import patch


@patch('yourapp.forms.geocoder.geocode')
def test_geocoding(self, mock_geocode):
    mock_geocode.return_value = Point(-122.4194, 37.7749, srid=4326)
    form_data = {
        'type': 'user',
        'city': 'San Francisco',
        'state': 'CA',
        'zip_code': '94103',
        'range': '10',
    }
    form = SearchForm(data=form_data)
    self.assertTrue(form.is_valid())
    self.assertIsNotNone(form.cleaned_data.get('location_point'))


from django.urls import reverse
from django.contrib.gis.geos import Point
from UserManagement.models import CustomUser
from PetManagement.models import Pet


class SearchViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = CustomUser.objects.create_user(username='john_doe', email='john@example.com', location=Point(1, 1))
        cls.user2 = CustomUser.objects.create_user(username='jane_doe', email='jane@example.com', location=Point(2, 2))
        Pet.objects.create(name='Rex', owner=cls.user1)
        Pet.objects.create(name='Buddy', owner=cls.user2)

    def test_search_by_user_name(self):
        response = self.client.get(reverse('UserManagement:search'), {'type': 'user', 'query': 'john_doe'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('users', response.context)
        users = response.context['users']
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].username, 'john_doe')

    def test_search_by_pet_id(self):
        rex = Pet.objects.get(name='Rex')
        response = self.client.get(reverse('UserManagement:search'), {'type': 'pet', 'pet_id': rex.id})
        self.assertEqual(response.status_code, 200)
        self.assertIn('pets', response.context)
        pets = response.context['pets']
        self.assertEqual(len(pets), 1)
        self.assertEqual(pets[0].name, 'Rex')
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        """
        Create and return a `User` with an email, username, and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        """
        Create and return a `User` with superuser (admin) permissions.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

    # Your existing UserManager methods here
