from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from PetManagement.serializers import PetSerializer
from .models import CustomUser, Friendship, Photo
from .utils import create_user


class CustomLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class CustomUserSerializer(GeoFeatureModelSerializer):
    password = serializers.CharField(write_only=True)
    pets = PetSerializer(many=True, required=False)
    location = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'password', 'first_name', 'last_name',
            'display_name', 'city', 'state', 'zip_code', 'has_pets', 'profile_incomplete',
            'preferred_language', 'profile_picture', 'pets', 'about_me',
            'slug', 'location'
        ]
        geo_field = 'location'
        read_only_fields = ['slug', 'profile_incomplete']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'display_name': {'required': True},
            'city': {'required': True},
            'state': {'required': True},
            'zip_code': {'required': True},
            'has_pets': {'required': True},
        }

    def get_location(self, obj):
        if obj.location:
            # Return GeoJSON format for the location
            return {
                "type": "Point",
                "coordinates": [obj.location.x, obj.location.y]
            }
        return None

    def create(self, validated_data):
        return create_user(self.Meta.model, validated_data)

    def get_pets(self, instance):
        from PetManagement.serializers import PetSerializer
        pets = instance.pets.all()
        return PetSerializer(pets, many=True).data

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
