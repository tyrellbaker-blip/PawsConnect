import os

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


def validate_image(file):
    valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
    ext = os.path.splitext(file.name)[1]
    if not ext.lower() in valid_extensions or file.size > 5242880:  # 5 MB max
        raise ValidationError('Unsupported file extension or file too large.')


class Post(models.Model):
    class VisibilityChoices(models.TextChoices):
        PUBLIC = 'public', _('public')
        FRIENDS_ONLY = 'friends_only', _('friends only')

    user = models.ForeignKey('UserManagement.CustomUser', on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    visibility = models.CharField(max_length=20, choices=VisibilityChoices.choices, default=VisibilityChoices.PUBLIC)
    tagged_pets = models.ManyToManyField('PetManagement.Pet', related_name='tagged_in_posts', blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Post by {self.user.username} on {self.timestamp}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('UserManagement.CustomUser', on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.id}"

    def deactivate(self):
        self.is_active = False
        self.save()


class Like(models.Model):
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey('UserManagement.CustomUser', related_name='likes', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Like by {self.user.username} on {self.post.id}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['post', 'user'], name='unique_like_per_user')
        ]
