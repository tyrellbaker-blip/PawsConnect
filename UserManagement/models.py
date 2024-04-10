import logging

from autoslug import AutoSlugField
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.measure import D
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


logger = logging.getLogger(__name__)


class Photo(models.Model):
    user = models.ForeignKey('CustomUser', related_name='user_photos', on_delete=models.CASCADE, null=True, blank=True)
    pet = models.ForeignKey('PetManagement.Pet', related_name='pet_photos', on_delete=models.CASCADE, null=True,
                            blank=True)
    image = models.ImageField(upload_to='photos/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        if self.user and self.pet:
            raise ValueError("A photo cannot be related to both a user and a pet.")
        super().save(*args, **kwargs)


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
    photos = models.ManyToManyField('Photo', related_name='tagged_users', blank=True)
    profile_incomplete = models.BooleanField(default=True)
    slug = AutoSlugField(populate_from='id', unique=True, always_update=True)

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
        return f"{self.username} {self.display_name} {self.first_name} {self.last_name} {self.city} {self.state} {self.zip_code}"

    @property
    def num_friends(self):
        return self.friends.count()

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = f"{self.first_name} {self.last_name}".strip()
        super().save(*args, **kwargs)

    def get_full_location(self):
        return f"{self.city}, {self.state} {self.zip_code}".strip()

    def get_profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return 'url/to/default/profile/picture'

    def get_absolute_url(self):
        return reverse('UserManagement:profile', kwargs={'slug': self.slug})

    @property
    def is_profile_private(self):
        return self.profile_visibility == 'noone'

    def add_friend(self, user):
        Friendship.objects.create(user_from=self, user_to=user)

    def remove_friend(self, user):
        Friendship.objects.filter(user_from=self, user_to=user).delete()

    def distance_to(self, other_user):
        if self.location and other_user.location:
            distance = self.location.distance(other_user.location) * D(mi=1)
            return distance.mi
        return None

    def set_profile_incomplete(user):
        required_fields = ['first_name', 'last_name', 'city', 'state', 'zip_code', 'profile_picture', 'has_pets']
        for field in required_fields:
            if not getattr(user, field):
                user.profile_incomplete = True
                user.save()
                return  # Exit the loop if any required field is missing

        user.profile_incomplete = False
        user.save()

    class Meta:
        indexes = [
            models.Index(fields=['location'], name='location_idx'),
        ]


class Friendship(models.Model):
    user_from = models.ForeignKey(CustomUser, related_name='sent_friendships', on_delete=models.CASCADE)
    user_to = models.ForeignKey(CustomUser, related_name='received_friendships', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20,
                              choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
                              default='pending')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_from', 'user_to'], name='unique_friendship')
        ]

    def __str__(self):
        return f"{self.user_from} -> {self.user_to}"


