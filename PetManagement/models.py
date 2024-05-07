from autoslug import AutoSlugField
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


def validate_image(file):
    valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
    ext = file.name.split('.')[-1]
    if ext.lower() not in valid_extensions or file.size > 5242880:  # 5 MB max
        raise ValidationError('Unsupported file extension or file too large.')


def pet_photo_path(instance, filename):
    # Generates a unique file path for each photo
    return f'pet_photos/{instance.pet.slug}/{filename}'


class PetManager(models.Manager):
    def search(self, pet_id=None, name=None, breed=None, age=None):
        queryset = self.get_queryset()
        if pet_id:
            queryset = queryset.filter(id=pet_id)
        if name:
            queryset = queryset.filter(name__icontains=name)
        if breed:
            queryset = queryset.filter(breed__icontains=breed)
        if age:
            queryset = queryset.filter(age=age)
        return queryset


class Pet(models.Model):
    class PetType(models.TextChoices):
        DOG = 'dog', 'Dog'
        CAT = 'cat', 'Cat'
        BIRD = 'bird', 'Bird'
        REPTILE = 'reptile', 'Reptile'
        OTHER = 'other', 'Other'

    owner = models.ForeignKey('UserManagement.CustomUser', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=50, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)  # Allows for unknown ages
    pet_type = models.CharField(max_length=20, choices=PetType.choices, default=PetType.OTHER)
    description = models.TextField(blank=True, max_length=500)
    profile_picture = models.ImageField(upload_to='pet_profile_pics/', validators=[validate_image], null=True,
                                        blank=True)
    slug = AutoSlugField(populate_from='name', unique=True)

    objects = PetManager()

    def get_absolute_url(self):
        return reverse('PetManagement:pet_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name

    def get_display_pet_type(self):
        """Returns a nicely formatted pet type for display."""
        return self.pet_type.capitalize()


class PetPhoto(models.Model):
    pet = models.ForeignKey(Pet, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=pet_photo_path, validators=[validate_image])
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo of {self.pet.name} uploaded on {self.uploaded_at.strftime('%Y-%m-%d')}"


class PetTransferRequest(models.Model):
    class TransferStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        CANCELED = 'canceled', 'Canceled'

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='transfer_requests')
    from_user = models.ForeignKey('UserManagement.CustomUser', related_name='sent_transfers', on_delete=models.CASCADE)
    to_user = models.ForeignKey('UserManagement.CustomUser', related_name='received_transfers',
                                on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=TransferStatus.choices, default=TransferStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Transfer of {self.pet.name} from {self.from_user.username} to {self.to_user.username}"
