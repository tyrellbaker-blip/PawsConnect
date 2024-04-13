from rest_framework import serializers

from UserManagement.serializers import CustomUserSerializer
from UserManagement.serializers import PetSerializer
from .models import Post, Comment, Like


class PostSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    tagged_pets = PetSerializer(many=True, read_only=True)
    visibility = serializers.ChoiceField(choices=Post.VisibilityChoices.choices)

    class Meta:
        model = Post
        fields = ['id', 'user', 'content', 'photo', 'visibility', 'tagged_pets', 'timestamp', 'updated_at', 'is_active']


class CommentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'timestamp', 'updated_at', 'is_active']


class LikeSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'timestamp', 'updated_at', 'is_active']
