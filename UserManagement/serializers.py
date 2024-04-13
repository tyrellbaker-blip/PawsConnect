# UserManagement/serializers.py
from rest_framework import serializers
from .models import CustomUser, Friendship
from PetManagement.serializers import PetSerializer

class CustomUserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'display_name', 'profile_picture', 'location']

class FriendshipSerializer(serializers.ModelSerializer):
    user_from = CustomUserSimpleSerializer(read_only=True)
    user_to = CustomUserSimpleSerializer(read_only=True)

    class Meta:
        model = Friendship
        fields = ['user_from', 'user_to', 'created_at', 'status']

class CustomUserSerializer(serializers.ModelSerializer):
    pets = PetSerializer(many=True, read_only=True)
    sent_friendships = FriendshipSerializer(many=True, read_only=True)
    received_friendships = FriendshipSerializer(many=True, read_only=True)
    preferred_language = serializers.ChoiceField(choices=CustomUser.LANGUAGE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ['username', 'display_name', 'profile_picture', 'location', 'pets', 'preferred_language',
                  'sent_friendships', 'received_friendships']

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate_email(self, value):
        if value and CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already used by another account.")
        return value