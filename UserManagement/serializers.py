from django.contrib.auth import get_user_model
from rest_framework import serializers

from PetManagement.models import Pet
from .models import CustomUser, Friendship, LANGUAGE_CHOICES, Photo


class CustomUserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'display_name', 'profile_picture', 'location', 'pets',
            'preferred_language', 'city', 'state', 'zip_code'
        ]
        can_edit_profile = serializers.SerializerMethodField()
        is_friend = serializers.SerializerMethodField()

    def get_can_edit_profile(self, instance):
        request = self.context.get('request')
        return instance == request.user

    def get_is_friend(self, instance):
        request = self.context.get('request')
        return Friendship.objects.filter(
            user_from=request.user, user_to=instance, status='accepted'
        ).exists()


class FriendshipSerializer(serializers.ModelSerializer):
    user_from = serializers.SlugRelatedField(slug_field='username', read_only=True)
    user_to = serializers.SlugRelatedField(slug_field='username', queryset=get_user_model().objects.all())

    class Meta:
        model = Friendship
        fields = ['user_from', 'user_to', 'created_at', 'status']


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'display_name', 'city', 'state', 'zip_code', 'has_pets', 'profile_incomplete',
            'preferred_language', 'profile_picture', 'pets'
        ]
        read_only_fields = ['profile_incomplete']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def get_pets(self, instance):
        from PetManagement.serializers import PetSerializer  # Import here to avoid circular dependency
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

    def get_can_edit_profile(self, instance):
        request = self.context.get('request')
        return instance == request.user  # Only allow editing own profile

    def get_is_friend(self, instance):
        request = self.context.get('request')
        return Friendship.objects.filter(
            user_from=request.user, user_to=instance, status='accepted'
        ).exists()


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'user', 'image', 'caption', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']
