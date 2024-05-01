from autoslug import AutoSlugField
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import GEOSGeometry
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
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

PROFILE_VISIBILITY_CHOICES = [
    ('public', 'Public'),
    ('friends', 'Friends'),
    ('private', 'Private'),
]

FRIENDSHIP_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('declined', 'Declined'),
]


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = models.CharField(_("username"), max_length=20, unique=True, blank=True)
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
    profile_visibility = models.CharField(max_length=10, choices=PROFILE_VISIBILITY_CHOICES, default='public')
    has_pets = models.BooleanField(_("has pets"), default=False)
    slug = AutoSlugField(_("slug"), populate_from='username', unique=True, always_update=False)
    location = gis_models.PointField(_("location"), geography=True, blank=True, null=True)
    city = models.CharField(_("city"), max_length=100, blank=True)
    state = models.CharField(_("state"), max_length=100, blank=True)
    zip_code = models.CharField(_("zip code"), max_length=12, blank=True)
    num_friends = models.PositiveIntegerField(default=0)
    pets = models.ManyToManyField('PetManagement.Pet', related_name='owners', blank=True)
    friends = models.ManyToManyField('self', symmetrical=False, related_name='user_friends', blank=True)
    email = models.EmailField(unique=True, null=False)
    about_me = models.TextField(_("about me"), blank=True)

    @property
    def get_location(self):
        if self.location:
            return GEOSGeometry(self.location, srid=self.location.srid)
        return None

    @property
    def outgoing_friend_requests(self):
        return self.sent_friendships.filter(status='pending')

    @property
    def incoming_friend_requests(self):
        return self.received_friendships.filter(status='pending')

    def get_absolute_url(self):
        return reverse('UserManagement:profile', kwargs={'slug': self.slug})

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def profile_changed(self, updated_data):
        """
        Checks if any of the profile fields have changed.
        Returns True if any of the profile fields have changed, False otherwise.
        """
        profile_fields = ['first_name', 'last_name', 'profile_picture', 'location', 'city', 'state', 'zip_code',
                          'has_pets', 'about_me']
        return any(getattr(self, field) != updated_data.get(field, getattr(self, field)) for field in profile_fields)


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
        return f"{self.user_from.username} -> {self.user_to.username} ({self.status})"

    def accept(self):
        self.status = 'accepted'
        self.save()

    def reject(self):
        self.status = 'rejected'
        self.save()


@receiver(post_save, sender=Friendship)
def update_friends_count(sender, instance, created, **kwargs):
    if instance.status == 'accepted' and not created:
        instance.user_from.num_friends += 1
        instance.user_from.save(update_fields=['num_friends'])
        instance.user_to.num_friends += 1
        instance.user_to.save(update_fields=['num_friends'])
