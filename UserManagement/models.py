from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    display_name = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    preferred_language = models.CharField(max_length=50, default='English')
