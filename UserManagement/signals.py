import logging

from django.contrib.gis.geos import Point
from django.db.models.signals import post_save
from django.dispatch import receiver
from geopy import GoogleV3

from PawsConnect.settings import GOOGLE_MAPS_API_KEY
from .models import CustomUser

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CustomUser)
def geocode_user_location(sender, instance, created, **kwargs):
    if not instance.location and instance.city and instance.state and instance.zip_code:
        # Attempt geocoding (similar logic as before)
        try:
            geolocator = GoogleV3(api_key=GOOGLE_MAPS_API_KEY)
            location_query = f"{instance.city}, {instance.state}, {instance.zip_code}"
            location = geolocator.geocode(location_query, timeout=10)

            if location:
                instance.location = Point(location.longitude, location.latitude)
                instance.save()
            else:
                # Send feedback to the user (e.g., email, notification)
                logger.warning(f"Geocoding failed for user {instance.username}: {location_query}")
                # You can implement logic here to notify the user about the failure
                # and potentially ask them to update their address information.
        except (GeocoderUnavailable, GeocoderTimedOut) as e:
            logger.error(f"Geocoding service error: {e}")
