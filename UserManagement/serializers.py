from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import CustomUser, Friendship, LANGUAGE_CHOICES

class CustomUserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'display_name', 'profile_picture',
                  'location', 'pets', 'preferred_language',
                  'sent_friendships', 'received_friendships','city', 'state', 'zip_code']

class FriendshipSerializer(serializers.ModelSerializer):
    user_from = serializers.PrimaryKeyRelatedField(read_only=True)
    user_to = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())

    class Meta:
        model = Friendship
        fields = ['user_from', 'user_to', 'created_at', 'status']

    def create(self, validated_data):
        return Friendship.objects.create(**validated_data)

class CustomUserSerializer(serializers.ModelSerializer):
    pets = serializers.SerializerMethodField()
    sent_friendships = FriendshipSerializer(many=True, read_only=True)
    received_friendships = FriendshipSerializer(many=True, read_only=True)
    preferred_language = serializers.ChoiceField(choices=LANGUAGE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ['username', 'display_name', 'profile_picture', 'location', 'pets', 'preferred_language',
                  'sent_friendships', 'received_friendships', 'num_friends']

    def get_pets(self, instance):
        from PetManagement.serializers import PetSerializer  # Import here to avoid circular dependency
        pets = instance.pets.all()
        return PetSerializer(pets, many=True).data

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate_email(self, value):
        if value and CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already used by another account.")
        return value
