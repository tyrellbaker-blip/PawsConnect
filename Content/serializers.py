# Content/serializers.py
from rest_framework import serializers

from PetManagement.models import Pet
from UserManagement.serializers import CustomUserSerializer
from .models import Post, Comment, Like


class PostSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    tagged_pets = serializers.PrimaryKeyRelatedField(
        queryset=Pet.objects.all(),
        many=True,
        required=False
    )
    visibility = serializers.ChoiceField(choices=Post.VisibilityChoices.choices)
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'user', 'content', 'photo', 'visibility', 'tagged_pets', 'timestamp', 'updated_at', 'is_active']

    def get_can_edit(self, instance):
        request = self.context.get('request')
        return instance.user == request.user

    def get_can_delete(self, instance):
        request = self.context.get('request')
        return instance.user == request.user

    def create(self, validated_data):
        tagged_pets = validated_data.pop('tagged_pets', [])
        post = Post.objects.create(**validated_data)
        post.tagged_pets.set(tagged_pets)
        return post

    def update(self, instance, validated_data):
        tagged_pets = validated_data.pop('tagged_pets', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if tagged_pets is not None:
            instance.tagged_pets.set(tagged_pets)
        instance.save()
        return instance


class CommentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
    tagged_pets = serializers.PrimaryKeyRelatedField(
        queryset=Pet.objects.all(),
        many=True,
        required=False  # Assuming not all comments need pet tags
    )
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'tagged_pets', 'timestamp', 'updated_at', 'is_active']

    def create(self, validated_data):
        tagged_pets = validated_data.pop('tagged_pets', [])
        comment = Comment.objects.create(**validated_data)
        comment.tagged_pets.set(tagged_pets)
        return comment

    def update(self, instance, validated_data):
        tagged_pets = validated_data.pop('tagged_pets', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if tagged_pets is not None:
            instance.tagged_pets.set(tagged_pets)
        instance.save()
        return instance

    def get_can_edit(self, instance):
        request = self.context.get('request')
        return instance.user == request.user

    def get_can_delete(self, instance):
        request = self.context.get('request')
        return instance.user == request.user or instance.post.user == request.user


class LikeSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'timestamp', 'updated_at', 'is_active']
