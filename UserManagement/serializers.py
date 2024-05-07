from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


from PetManagement.serializers import PetSerializer
from .geocoding import geocode_address
from .models import CustomUser, Friendship, Photo

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    pets = PetSerializer(many=True, read_only=True)
    profile_picture = serializers.ImageField(use_url=True, required=False, allow_null=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'}, required=False)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'password', 'first_name', 'last_name',
            'display_name', 'city', 'state', 'zip_code', 'has_pets',
            'preferred_language', 'profile_picture', 'pets', 'about_me', 'slug', 'has_completed_profile'
        ]
        read_only_fields = ['id', 'slug', 'has_completed_profile']

    def create(self, validated_data):
        from PetManagement.models import Pet
        display_name = validated_data.pop('display_name', None) or validated_data.get('username')
        validated_data['display_name'] = display_name

        address_components = ('city', 'state', 'zip_code')
        if all(validated_data.get(component) for component in address_components):
            try:
                location = geocode_address(**{comp: validated_data[comp] for comp in address_components})
                validated_data['location'] = location
            except Exception as e:
                raise ValidationError({'address': 'Invalid address.'})

        pets_data = validated_data.pop('pets', [])
        user = User.objects.create(**validated_data)

        if validated_data.get('has_pets', False) and pets_data:
            for pet_data in pets_data:
                Pet.objects.create(owner=user, **pet_data)

        return user

    def update(self, instance, validated_data):
        from PetManagement.models import Pet
        pets_data = validated_data.pop('pets', [])
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)

        if password:
            instance.set_password(password)

        if instance.has_pets and pets_data:
            for pet_data in pets_data:
                Pet.objects.create(owner=instance, **pet_data)

        instance.save()
        return instance


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


class CompleteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'display_name',
            'about_me',
            'preferred_language',
            'profile_picture',
            'profile_visibility',
            'city',
            'state',
            'zip_code',
            'location',
        ]

    def update(self, instance, validated_data):
        instance.display_name = validated_data.get('display_name', instance.display_name)
        instance.about_me = validated_data.get('about_me', instance.about_me)
        instance.preferred_language = validated_data.get('preferred_language', instance.preferred_language)
        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
        instance.profile_visibility = validated_data.get('profile_visibility', instance.profile_visibility)
        instance.city = validated_data.get('city', instance.city)
        instance.state = validated_data.get('state', instance.state)
        instance.zip_code = validated_data.get('zip_code', instance.zip_code)
        instance.location = validated_data.get('location', instance.location)
        instance.has_completed_profile = True  # Set the flag to indicate profile completion
        instance.save()
        return instance
