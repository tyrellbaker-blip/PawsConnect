from django.contrib.auth import get_user_model
from rest_framework import serializers

from PetManagement.serializers import PetSerializer
from .models import CustomUser, Friendship, Photo
from .utils import create_user


class CustomLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    pets = PetSerializer(many=True, required=False)

    class Meta:
        model = get_user_model()  # Ensures we're using the current user model
        fields = [
            'id', 'email', 'password', 'first_name', 'last_name',
            'display_name', 'city', 'state', 'zip_code', 'has_pets',
            'preferred_language', 'profile_picture', 'pets', 'about_me', 'slug'
        ]
        read_only_fields = ['slug']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'display_name': {'required': True},
            'city': {'required': True},
            'state': {'required': True},
            'zip_code': {'required': True},
            'has_pets': {'required': True}
        }

    def create(self, validated_data):
        return create_user(self.Meta.model, validated_data)

    def update(self, instance, validated_data):
        # Handle the update logic, ensuring sensitive fields like password are handled correctly
        instance = super().update(instance, validated_data)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            instance.save()
        return instance

    def get_pets(self, instance):
        from PetManagement.serializers import PetSerializer
        pets = instance.pets.all()
        return PetSerializer(pets, many=True).data

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already used by another account.")
        return value


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
