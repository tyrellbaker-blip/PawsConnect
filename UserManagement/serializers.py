from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from PetManagement.serializers import PetSerializer
from .geocoding import geocode_address
from .models import CustomUser, Friendship, Photo

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    pets = PetSerializer(many=True, read_only=True)
    posts = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    profile_picture = serializers.ImageField(use_url=True, required=False, allow_null=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'}, required=False)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'password', 'first_name', 'last_name',
            'display_name', 'city', 'state', 'zip_code', 'has_pets',
            'preferred_language', 'profile_picture', 'pets', 'posts', 'comments',
            'about_me', 'slug', 'has_completed_profile'
        ]
        read_only_fields = ['id', 'slug', 'has_completed_profile']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save()

        city = validated_data.get('city')
        state = validated_data.get('state')
        zip_code = validated_data.get('zip_code')

        if city or state or zip_code:
            try:
                location = geocode_address(city=city, state=state, zip_code=zip_code)
                instance.location = location
                instance.save()
            except Exception as e:
                raise ValidationError({'address': 'Invalid address.'})

        return instance

    def get_posts(self, obj):
        from Content.serializers import PostSerializer
        return PostSerializer(obj.posts.all(), many=True).data

    def get_comments(self, obj):
        from Content.serializers import CommentSerializer
        return CommentSerializer(obj.comments.all(), many=True).data


class FriendshipSerializer(serializers.ModelSerializer):
    user_from = serializers.SlugRelatedField(slug_field='username', read_only=True)
    user_to = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = Friendship
        fields = ['id', 'user_from', 'user_to', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']


class PhotoSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Photo
        fields = ['id', 'user', 'image', 'caption', 'uploaded_at']
        read_only_fields = ['id', 'user', 'uploaded_at']
