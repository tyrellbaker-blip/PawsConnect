import logging

from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db import models
from django.utils.translation import gettext_lazy as _
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut
from geopy.geocoders import GoogleV3
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

# Replace 'my_project.settings' with your actual settings module
from PawsConnect.settings import GOOGLE_MAPS_API_KEY

logger = logging.getLogger(__name__)


class CustomUser(AbstractUser):
    city = models.CharField(_("city"), max_length=100, blank=True)
    state = models.CharField(_("state"), max_length=100, blank=True)
    zip_code = models.CharField(_("zip code"), max_length=12, blank=True)
    location = gis_models.PointField(geography=True, blank=True, null=True)
    profile_picture = ProcessedImageField(
        upload_to='profile_pics/',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 60},
        blank=True,
        null=True
    )
    display_name = models.CharField(_("display name"), max_length=100, db_index=True)
    preferred_language = models.CharField(_("preferred language"), max_length=5, default='en')
    profile_visibility = models.CharField(
        _("profile visibility"),
        max_length=10,
        choices=[('everyone', 'Everyone'), ('friends', 'Friends'), ('noone', 'No One')],
        default='everyone'
    )
    about_me = models.TextField(_("about me"), blank=True, max_length=500, null=True)
    has_pets = models.BooleanField(default=False)
    friends = models.ManyToManyField('self', through='Friendship', symmetrical=False, related_name='friends_rel')

    # --- Properties for Derived Information ---
    @property
    def pets(self):
        from PetManagement.models import Pet
        return Pet.objects.filter(owner=self)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def location_string(self):
        return self.get_full_location()

    @property
    def searchable_fields(self):
        return 'username', 'display_name', 'first_name', 'last_name', 'city', 'state', 'zip_code'

    @property
    def searchable_text(self):
        """
        Combines relevant fields into a single string for easier full-text search.
        """
        return f"{self.username} {self.display_name} {self.first_name} {self.last_name} {self.city} {self.state} {self.zip_code}"

    @property
    def num_friends(self):
        return self.friends.count()

# --- Utility Methods ---
    def save(self, *args, **kwargs):
        # Default display name if blank
        if not self.display_name:
            self.display_name = f"{self.first_name} {self.last_name}".strip()

        # Geocoding logic
        if not self.location and self.city and self.state and self.zip_code:
            try:
                geolocator = GoogleV3(api_key=GOOGLE_MAPS_API_KEY)
                location_query = f"{self.city}, {self.state}, {self.zip_code}"
                location = geolocator.geocode(location_query, timeout=10)

                if location:
                    self.location = Point(location.longitude, location.latitude)
                else:
                    logger.warning(f"Geocoding failed for: {location_query}")
            except (GeocoderUnavailable, GeocoderTimedOut) as e:
                logger.error(f"Geocoding service error: {e}")

        super().save(*args, **kwargs)

    def get_full_location(self):
        """Returns a string of the full location based on city, state, and zip."""
        return f"{self.city}, {self.state} {self.zip_code}".strip()

    def get_profile_picture_url(self):
        """Returns the URL of the profile picture or a placeholder if none."""
        if self.profile_picture:
            return self.profile_picture.url
        return 'url/to/default/profile/picture'

    @property
    def is_profile_private(self):
        """Checks if the user's profile is set to private."""
        return self.profile_visibility == 'noone'

    def add_friend(self, user):
        Friendship.objects.create(from_user=self, to_user=user)

    def remove_friend(self, user):
        Friendship.objects.filter(from_user=self, to_user=user).delete()

    def distance_to(self, other_user):
        """
        Calculates the distance (in miles) between two users based on their location coordinates.
        """
        if self.location and other_user.location:
            distance = self.location.distance(other_user.location) * D(mi=1)
            return distance.mi
        return None

    class Meta:
        indexes = [
            models.Index(fields=['location'], name='location_idx'),
        ]


# Assuming the Friendship model is part of UserManagement and reflects user connections
class Friendship(models.Model):
    user_from = models.ForeignKey(CustomUser, related_name='friendship_creator_set', on_delete=models.CASCADE)
    user_to = models.ForeignKey(CustomUser, related_name='friend_set', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_from', 'user_to'], name='unique_friendship')
        ]

    def __str__(self):
        return f"{self.user_from} -> {self.user_to}"
