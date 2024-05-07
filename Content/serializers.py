# Content/serializers.py
from rest_framework import serializers

from .models import Post, Comment, Like


class PostSerializer(serializers.ModelSerializer):
    visibility = serializers.ChoiceField(choices=Post.VisibilityChoices.choices)
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    photo = serializers.ImageField(required=False, allow_null=True)
    user = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'user', 'content', 'photo', 'visibility', 'tagged_pets', 'timestamp', 'updated_at',
            'is_active', 'can_edit', 'can_delete'
        ]
        read_only_fields = ['user', 'timestamp', 'updated_at']

    def get_user(self, obj):
        from UserManagement.serializers import CustomUserSerializer
        return CustomUserSerializer(obj.user, read_only=True).data

    def get_can_edit(self, obj):
        request = self.context.get('request')
        if obj is None:
            return False
        return obj.user == request.user

    def get_can_delete(self, obj):
        request = self.context.get('request')
        if obj is None:
            return False
        return obj.user == request.user


class CommentSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'user', 'content', 'tagged_pets', 'timestamp', 'updated_at', 'is_active'
        ]

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
    user = serializers.SerializerMethodField()
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'timestamp']

    def get_user(self, obj):
        from UserManagement.serializers import CustomUserSerializer
        return CustomUserSerializer(obj.user, read_only=True).data
