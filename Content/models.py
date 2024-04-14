from django.db import models


class Post(models.Model):
    class VisibilityChoices(models.TextChoices):
        PUBLIC = 'Public', 'Public'
        FRIENDS_ONLY = 'Friends Only', 'Friends Only'

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey('UserManagement.CustomUser', on_delete=models.CASCADE, related_name='posts')
    tagged_pets = models.ManyToManyField('PetManagement.Pet',related_name='posts', blank=True)
    content = models.TextField()
    photo = models.ImageField(upload_to='post_photos/', null=True, blank=True)
    visibility = models.CharField(max_length=20, choices=VisibilityChoices.choices, default=VisibilityChoices.PUBLIC)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Post by {self.user.username} on {self.timestamp}"


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey('UserManagement.CustomUser', related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.id}"


class Like(models.Model):
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey('UserManagement.CustomUser', related_name='likes', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Like by {self.user.username} on {self.post.id}"
