from django.contrib.auth import get_user_model
from rest_framework import serializers

from PetManagement.models import Pet
from PetManagement.serializers import PetSerializer
from .models import Friendship, Photo


class CustomLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


from rest_framework import serializers
from .models import CustomUser
from .geocoding import geocode_address


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    pets = PetSerializer(many=True, required=False)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'password', 'first_name', 'last_name',
            'display_name', 'city', 'state', 'zip_code', 'has_pets',
            'preferred_language', 'profile_picture', 'pets', 'about_me', 'slug'
        ]
        read_only_fields = ['slug']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'display_name': {'required': False},
            'city': {'required': True},
            'state': {'required': True},
            'zip_code': {'required': True},
            'has_pets': {'required': True}
        }

    def create(self, validated_data):
        pets_data = validated_data.pop('pets', [])
        password = validated_data.pop('password')
        display_name = validated_data.pop('display_name', None)

        # Set display_name to username if not provided
        if not display_name:
            validated_data['display_name'] = validated_data['username']

        # Geocode the address
        city = validated_data.get('city')
        state = validated_data.get('state')
        zip_code = validated_data.get('zip_code')
        if city and state and zip_code:
            location = geocode_address(city, state, zip_code)
            validated_data['location'] = location

        # Create user instance
        user = CustomUser.objects.create(
            **validated_data
        )
        user.set_password(password)
        user.save()

        # Create associated pets
        for pet_data in pets_data:
            Pet.objects.create(owner=user, **pet_data)

        return user


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
