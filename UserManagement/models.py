from autoslug import AutoSlugField
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.db.models import F
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill



# Constants for choices
LANGUAGE_CHOICES = [
    ('en', 'English'), ('es', 'Spanish'), ('fr', 'French'),
    ('de', 'German'), ('it', 'Italian'),
]
PROFILE_VISIBILITY_CHOICES = [
    ('public', 'Public'), ('friends', 'Friends'), ('private', 'Private'),
]
FRIENDSHIP_STATUS_CHOICES = [
    ('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined'),
]


class CustomUserManager(BaseUserManager):
    def create(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not extra_fields.get('is_staff') or not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_staff=True and is_superuser=True.')
        return self.create(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = models.CharField(_("username"), max_length=20, unique=True)
    display_name = models.CharField(_("display name"), max_length=100, db_index=True)
    about_me = models.TextField(_("about me"), blank=True, null=True)
    preferred_language = models.CharField(_("preferred language"), choices=LANGUAGE_CHOICES, default='en', max_length=5)
    profile_picture = ProcessedImageField(
        upload_to='profile_pics/', processors=[ResizeToFill(300, 300)],
        format='JPEG', options={'quality': 60}, blank=True, null=True
    )
    profile_visibility = models.CharField(choices=PROFILE_VISIBILITY_CHOICES, default='public', max_length=10)
    has_pets = models.BooleanField(_("has pets"), default=False)
    slug = AutoSlugField(populate_from='username', unique=True)
    location = gis_models.PointField(_("location"), geography=True, blank=True, null=True)
    city = models.CharField(_("city"), max_length=100, blank=True)
    state = models.CharField(_("state"), max_length=100, blank=True)
    zip_code = models.CharField(_("zip code"), max_length=12, blank=True)
    num_friends = models.PositiveIntegerField(default=0)
    pets = models.ManyToManyField('PetManagement.Pet', related_name='owned_by', blank=True)
    friends = models.ManyToManyField('self', related_name='friends_with', symmetrical=False, blank=True)
    email = models.EmailField(unique=True)
    has_completed_profile = models.BooleanField(default=False)

    objects = CustomUserManager()

    def get_absolute_url(self):
        return reverse('user_profile', kwargs={'slug': self.slug})

    def __str__(self):
        return self.username


class Photo(models.Model):
    user = models.ForeignKey(CustomUser, related_name='user_photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo by {self.user.username}"


class Friendship(models.Model):
    user_from = models.ForeignKey(CustomUser, related_name='sent_friendships', on_delete=models.CASCADE)
    user_to = models.ForeignKey(CustomUser, related_name='received_friendships', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=FRIENDSHIP_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

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


def increment_friend_count(user_from, user_to):
    CustomUser.objects.filter(pk=user_from.pk).update(num_friends=F('num_friends') + 1)
    CustomUser.objects.filter(pk=user_to.pk).update(num_friends=F('num_friends') + 1)

def decrement_friend_count(user_from, user_to):
    CustomUser.objects.filter(pk=user_from.pk).update(num_friends=F('num_friends') - 1)
    CustomUser.objects.filter(pk=user_to.pk).update(num_friends=F('num_friends') - 1)


@receiver(post_save, sender=Friendship)
def update_friends_count_on_save(sender, instance, created, **kwargs):
    if created and instance.status == 'accepted':
        increment_friend_count(instance.user_from, instance.user_to)

@receiver(post_delete, sender=Friendship)
def update_friends_count_on_delete(sender, instance, **kwargs):
    if instance.status == 'accepted':
        decrement_friend_count(instance.user_from, instance.user_to)
