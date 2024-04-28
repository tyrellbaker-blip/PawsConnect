import logging
import signal

from allauth.account.signals import user_signed_up
from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.sessions.models import Session
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import GoogleV3

from PetManagement.models import PetProfile, Pet
from .models import CustomUser  # Ensure this matches your user model import

# Setup logger
logger = logging.getLogger(__name__)


# Geocode user location on user model update
@receiver(post_save, sender=CustomUser)
def geocode_user_location(sender, instance=None, created=False, **kwargs):
    if instance and created and not instance.location and instance.city and instance.state and instance.zip_code:
        try:
            geolocator = GoogleV3(api_key=settings.GOOGLE_MAPS_API_KEY)
            address = f"{instance.city}, {instance.state}, {instance.zip_code}"
            location = geolocator.geocode(address)

            if location:
                instance.location = Point(location.longitude, location.latitude)
                instance.save()  # Update the instance
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            logger.error(f"Geocoding error for user {instance.pk}: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during geocoding: {e}")


# Clear all sessions on shutdown
def clear_sessions_on_shutdown(signum, frame):
    logger.info("Received SIGTERM signal. Clearing all sessions...")
    Session.objects.all().delete()


# Connect the SIGTERM signal to the clear_sessions_on_shutdown function
# This could be placed within an AppConfig.ready() method, or similarly, here for simplicity
signal.signal(signal.SIGTERM, clear_sessions_on_shutdown)


# Optional: YourAppConfig ready method if you're using AppConfig to connect signals

@receiver(user_signed_up)
def mark_profile_incomplete(sender, **kwargs):
    user = kwargs.pop('user')
    CustomUser.objects.filter(pk=user.pk).update(profile_incomplete=True, slug=F('slug'))



@receiver(post_save, sender=Pet)
def create_pet_profile(sender, instance, created, **kwargs):
    if created:
        PetProfile.objects.create(pet=instance)
