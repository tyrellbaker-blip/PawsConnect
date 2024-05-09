# Content/serializers.py
from rest_framework import serializers

from PetManagement.models import Pet
from PetManagement.serializers import PetSerializer
from UserManagement.serializers import CustomUserSerializer
from .models import Post, Comment, Like


class CommentSerializer:
    pass


class LikeSerializer:
    pass


class PostSerializer(serializers.ModelSerializer):
    tagged_pets = PetSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes = LikeSerializer(many=True, read_only=True)
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'content', 'visibility', 'tagged_pets', 'timestamp', 'updated_at', 'is_active', 'comments', 'likes']
        read_only_fields = ['id', 'user', 'timestamp', 'updated_at', 'is_active', 'comments', 'likes']

    def create(self, validated_data):
        tagged_pets_data = self.context['request'].data.get('tagged_pets', [])
        post = Post.objects.create(user=self.context['request'].user, **validated_data)
        for pet_id in tagged_pets_data:
            pet = Pet.objects.get(id=pet_id)
            post.tagged_pets.add(pet)
        return post


class CommentSerializer(serializers.ModelSerializer):
    from UserManagement.serializers import CustomUserSerializer
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'timestamp', 'updated_at', 'is_active']
        read_only_fields = ['id', 'post', 'user', 'timestamp', 'updated_at', 'is_active']

    def get_user(self, obj):
        from UserManagement.serializers import CustomUserSerializer
        return CustomUserSerializer(obj.user, read_only=True).data

    def get_can_edit(self, obj):
        request = self.context.get('request', None)
        if request and hasattr(request, 'user') and request.user:
            return obj.user == request.user
        return False

    def get_can_delete(self, instance):
        request = self.context.get('request', None)
        if request and hasattr(request, 'user') and request.user:
            return instance.user == request.user or (hasattr(instance, 'post') and instance.post.user == request.user)
        return False


class LikeSerializer(serializers.ModelSerializer):
    from UserManagement.serializers import CustomUserSerializer
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'timestamp']
        read_only_fields = ['id', 'post', 'user', 'timestamp']
