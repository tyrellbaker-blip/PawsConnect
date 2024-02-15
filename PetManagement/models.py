from django.db import models

from UserManagement.models import CustomUser


class Pet(models.Model):
    owner = models.ForeignKey(CustomUser, related_name='pets', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to='pet_pics/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    breed = models.CharField(max_length=255, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)