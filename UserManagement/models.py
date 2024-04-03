from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.db import models
from UserManagement.utils import get_lat_lon_from_address


class CustomUser(AbstractUser):
    display_name = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    location = gis_models.PointField(null=True, blank=True)  # Note the use of gis_models here
    preferred_language = models.CharField(max_length=50, default='English')
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)
    zip_code = models.CharField(max_length=5, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Geocode to update location if city, state, or zip have changed
        if self.city and self.state and self.zip_code and not self.location:
            latitude, longitude = get_lat_lon_from_address(self.city, self.state, self.zip_code)
            if latitude and longitude:
                self.location = Point(longitude, latitude)
        super().save(*args, **kwargs)
