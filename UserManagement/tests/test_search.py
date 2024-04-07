from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from PetManagement.models import Pet
from UserManagement.forms import SearchForm
from UserManagement.models import CustomUser


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
            # Providing partial location information
            'city': 'Some City',
            # Intentionally omitting 'state' and 'zip_code'
        }
        form = SearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Please provide a complete address: city, state, and zip code for location-based searches.',
                      form.errors['__all__'])


def test_missing_required_fields(self):
    form_data = {
        # Omitting required fields like 'type'
        'city': 'San Francisco',
        'range': '10',
    }
    form = SearchForm(data=form_data)
    self.assertFalse(form.is_valid())
    self.assertIn('type', form.errors)





@patch('yourapp.forms.geocoder.geocode')
def test_geocoding(self, mock_geocode):
    # Mock the geocoder response
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

    # Assuming _geocode_location method sets 'location_point' in cleaned_data
    self.assertIsNotNone(form.cleaned_data.get('location_point'))


class SearchViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Setup test data
        user1 = CustomUser.objects.create_user(username='john_doe', display_name='John Doe', email='john@example.com',
                                               location=Point(1, 1))
        user2 = CustomUser.objects.create_user(username='jane_doe', display_name='Jane Smith', email='jane@example.com',
                                               location=Point(2, 2))
        Pet.objects.create(name='Rex', owner=user1, id='1')
        Pet.objects.create(name='Buddy', owner=user2, id='2')

    def test_search_by_user_name(self):
        response = self.client.get(reverse('UserManagement:search'), {'type': 'user', 'query': 'john_doe'})
        self.assertIs(response.status_code, 200)
        self.assertIn('users', response.context)
        users = response.context['users']
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].username, 'john_doe')

    def test_search_by_pet_id(self):
        response = self.client.get(reverse('UserManagement:search'), {'type': 'pet', 'pet_id': '1'})
        self.assertIs(response.status_code, 200)
        self.assertIn('pets', response.context)
        pets = response.context['pets']
        self.assertEqual(len(pets), 1)
        self.assertEqual(pets[0].name, 'Rex')


class DistanceSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # User in Daly City (within 10 miles of San Francisco)
        cls.user_near = CustomUser.objects.create_user(
            username='user_near',
            email='usernear@example.com',
            password='test',
            location=Point(-122.4702, 37.6879, srid=4326)
        )

        # User in Sacramento (beyond 10 miles from San Francisco)
        cls.user_far = CustomUser.objects.create_user(
            username='user_far',
            email='userfar@example.com',
            password='test',
            location=Point(-121.4944, 38.5816, srid=4326)
        )

    def test_distance_search_within_10_miles(self):
        # Searches for users within 10 miles of San Francisco
        response = self.client.get(reverse('UserManagement:search'), {
            'type': 'user',
            'city': 'San Francisco',
            'state': 'CA',
            'zip_code': '94102',  # Zip code for San Francisco for geocoding
            'range': '10',
        })
        self.assertEqual(response.status_code, 200)
        users = response.context['users']
        self.assertIn(self.user_near, users)  # Daly City user should be included
        self.assertNotIn(self.user_far, users)  # Sacramento user should be excluded
