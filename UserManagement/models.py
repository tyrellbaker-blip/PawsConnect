from autoslug import AutoSlugField
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis_models
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
    profile_visibility = models.CharField(max_length=10, choices=PROFILE_VISIBILITY_CHOICES, default='public')
    has_pets = models.BooleanField(default=False)
    profile_incomplete = models.BooleanField(default=True)
    slug = AutoSlugField(populate_from='username', unique=True)
    location = gis_models.PointField(_("location"), blank=True, null=True)
    city = models.CharField(_("city"), max_length=100, blank=True)
    state = models.CharField(_("state"), max_length=100, blank=True)
    zip_code = models.CharField(_("zip code"), max_length=12, blank=True)
    num_friends = models.PositiveIntegerField(default=0)
    pets = models.ManyToManyField('PetManagement.Pet', related_name='owners', blank=True)
    friends = models.ManyToManyField('self', symmetrical=False, related_name='user_friends', blank=True)
    email = models.EmailField(unique=True, null=False)
    about_me = models.TextField(_("about me"), blank=True)

    @property
    def outgoing_friend_requests(self):
        return self.sent_friendships.filter(status='pending')

    @property
    def incoming_friend_requests(self):
        return self.received_friendships.filter(status='pending')

    def get_absolute_url(self):
        return reverse('UserManagement:profile', kwargs={'slug': self.slug})

    @property
    def is_profile_complete(self):
        required_fields = ['first_name', 'last_name', 'profile_picture', 'has_pets']
        return all(getattr(self, field) for field in required_fields)

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

    def set_profile_incomplete(self):
        required_fields = ['first_name', 'last_name', 'city', 'state', 'zip_code', 'has_pets']
        if all(getattr(self, field) for field in required_fields):
            self.profile_incomplete = False
        else:
            self.profile_incomplete = True
        self.save()


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
