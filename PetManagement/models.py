from django.db import models

from UserManagement.models import CustomUser


class Pet(models.Model):
    PET_TYPE_CHOICES = [
        ('dog', 'Dog'),
        ('cat', 'Cat'),
        ('bird', 'Bird'),
        ('rep', 'Reptile'),
        ('oth', 'Other'),
    ]
    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=255, db_index=True)
    pet_type = models.CharField(max_length=20, choices=PET_TYPE_CHOICES, default='dog')
    profile_picture = models.ImageField(upload_to='pet_pics/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    breed = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    posts = models.ManyToManyField('Content.Post', related_name='tagged_pets', blank=True)

    @property
    def searchable_fields(self):
        return 'name', 'breed'  # Add 'pet_type' if needed

    @property
    def searchable_text(self):
        return f"{self.name} {self.breed}"  # Add 'pet_type' if needed

    @property
    def profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return None
