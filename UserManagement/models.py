from autoslug import AutoSlugField
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

LANGUAGE_CHOICES = [
    ('en', 'English'),
    ('es', 'Spanish'),
    ('fr', 'French'),
    ('de', 'German'),
    ('it', 'Italian'),
]

FRIENDSHIP_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('declined', 'Declined'),
]


class UserManager(models.Manager):
    def search(self, query=None, location_point=None, search_range=None):
        queryset = self.get_queryset()
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query) |
                Q(display_name__icontains=query)
            )
        if location_point and search_range:
            search_distance = D(mi=search_range)
            queryset = queryset.annotate(
                distance=Distance('location', location_point)
            ).filter(location__distance_lte=(location_point, search_distance))
        return queryset


class CustomUser(AbstractUser):
    display_name = models.CharField(_("display name"), max_length=100, db_index=True)
    preferred_language = models.CharField(_("preferred language"), max_length=5, choices=LANGUAGE_CHOICES, default='en')
    profile_picture = ProcessedImageField(
        upload_to='profile_pics/',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 60},
        blank=True,
        null=True
    )

    has_pets = models.BooleanField(default=False)
    profile_incomplete = models.BooleanField(default=True)
    slug = AutoSlugField(populate_from='username', unique=True)
    location = gis_models.PointField(_("location"), blank=True, null=True)
    first_name = models.CharField(_("first name"), max_length=30, blank=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True)
    city = models.CharField(_("city"), max_length=100, blank=True)
    state = models.CharField(_("state"), max_length=100, blank=True)
    zip_code = models.CharField(_("zip code"), max_length=12, blank=True)

    objects = UserManager()

    def get_absolute_url(self):
        return reverse('UserManagement:profile', kwargs={'slug': self.slug})

    @property
    def is_profile_complete(self):
        required_fields = ['first_name', 'last_name', 'profile_picture', 'has_pets']
        return all(getattr(self, field) for field in required_fields)




class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    location = models.CharField(max_length=100, blank=True)
    friends = models.ManyToManyField('self', symmetrical=False, related_name='user_friends', blank=True)
    about_me = models.TextField(_("about me"), blank=True, max_length=500, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Photo(models.Model):
    user = models.ForeignKey(CustomUser, related_name='user_photos', on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='photos/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo by {self.user.username}"


class Friendship(models.Model):
    user_from = models.ForeignKey(CustomUser, related_name='sent_friendships', on_delete=models.CASCADE)
    user_to = models.ForeignKey(CustomUser, related_name='received_friendships', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=FRIENDSHIP_STATUS_CHOICES, default='pending')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_from', 'user_to'], name='unique_friendship')
        ]

    def __str__(self):
        return f"{self.user_from.username} -> {self.user_to.username}"
