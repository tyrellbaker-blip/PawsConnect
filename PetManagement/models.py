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
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='pets')
    name = models.CharField(max_length=255, db_index=True)
    pet_type = models.CharField(max_length=20, choices=PET_TYPE_CHOICES, default='dog')
    profile_picture = models.ImageField(upload_to='pet_pics/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    breed = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)

    @property
    def searchable_fields(self):
        return 'id', 'name', 'breed', 'pet_type'

    @property
    def searchable_text(self):
        return f"{self.name} {self.breed} {self.pet_type}, {self.id}, "

    @property
    def profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return None


class PetTransferRequest(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='transfer_requests')
    from_user = models.ForeignKey(CustomUser, related_name='sent_transfers', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name='received_transfers', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Transfer of {self.pet.name} from {self.from_user.username} to {self.to_user.username}"