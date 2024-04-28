from django.contrib.auth import get_user_model
from rest_framework import serializers

from Content.serializers import PostSerializer
from PetManagement.models import Pet
from PetManagement.serializers import PetSerializer
from .models import CustomUser, Friendship, Photo


class CustomLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    pets = PetSerializer(many=True, required=False)
    profile_complete = serializers.SerializerMethodField()
    posts = PostSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'password', 'first_name', 'last_name',
            'display_name', 'city', 'state', 'zip_code', 'has_pets', 'profile_incomplete',
            'preferred_language', 'profile_picture', 'pets', 'about_me', 'location',
            'profile_complete', 'posts'
        ]
        read_only_fields = ['profile_incomplete']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        pets_data = validated_data.pop('pets', [])
        user = CustomUser.objects.create_user(**validated_data)
        for pet_data in pets_data:
            Pet.objects.create(owner=user, **pet_data)
        return user

    def get_pets(self, instance):
        from PetManagement.serializers import PetSerializer
        pets = instance.pets.all()
        return PetSerializer(pets, many=True).data

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already used by another account.")
        return value

    def get_profile_complete(self, instance):
        required_fields = ['first_name', 'last_name', 'profile_picture', 'location', 'city', 'state', 'zip_code',
                           'has_pets', 'about_me']
        return not instance.profile_incomplete and all(getattr(instance, field) for field in required_fields)


class FriendshipSerializer(serializers.ModelSerializer):
    user_from = serializers.SlugRelatedField(slug_field='username', read_only=True)
    user_to = serializers.SlugRelatedField(slug_field='username', queryset=get_user_model().objects.all())

    class Meta:
        model = Friendship
        fields = ['user_from', 'user_to', 'created_at', 'status']


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'user', 'image', 'caption', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']
