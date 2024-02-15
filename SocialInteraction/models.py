from django.db import models

from PetManagement.models import Pet
from UserManagement.models import CustomUser


class Post(models.Model):
    class VisibilityChoices(models.TextChoices):
        PUBLIC = 'Public', 'Public'
        FRIENDS_ONLY = 'Friends Only', 'Friends Only'

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(CustomUser, related_name='posts', on_delete=models.CASCADE)
    content = models.TextField()
    photo = models.ImageField(upload_to='post_photos/', null=True, blank=True)
    visibility = models.CharField(max_length=50, choices=[('Public', 'Public'), ('Friends Only', 'Friends Only')])
    tagged_pets = models.ManyToManyField(Pet, related_name='posts', blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Post by {self.user.username} on {self.timestamp}"


class PetTransferRequest(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='transfer_requests')
    from_user = models.ForeignKey(CustomUser, related_name='sent_transfers', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name='received_transfers', on_delete=models.CASCADE)
    status = models.CharField(max_length=50,
                              choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Denied', 'Denied')])
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Transfer of {self.pet.name} from {self.from_user.username} to {self.to_user.username}"


class Friendship(models.Model):
    from_user = models.ForeignKey(CustomUser, related_name='friendships', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name='_unused_friend_relation', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username}"


CustomUser.add_to_class('friends', models.ManyToManyField('self', through=Friendship, symmetrical=False,
                                                          related_name='friends_rel'))


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.id}"


class Like(models.Model):
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, related_name='likes', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Like by {self.user.username} on {self.post.id}"
