from django.contrib.gis.geos import Point
from django.test import TestCase
from unittest.mock import patch, MagicMock
from UserManagement.models import CustomUser

class CustomUserModelTest(TestCase):

    @patch('UserManagement.models.GoogleV3.geocode')
    def test_geocoding_on_save(self, mock_geocode):
        # Set up the mock object to return a Location object with latitude and longitude attributes
        mock_location = MagicMock()
        mock_location.latitude = 39.7392
        mock_location.longitude = -104.9903
        mock_geocode.return_value = mock_location

        # Proceed with creating a user to trigger the save method
        user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123',
            city='Denver',
            state='Colorado',
            zip_code='80202'
        )
        user.save()

        # Check if the geocoding logic correctly updated the user's location
        self.assertAlmostEqual(user.location.x, -104.9903, places=5)
        self.assertAlmostEqual(user.location.y, 39.7392, places=5)