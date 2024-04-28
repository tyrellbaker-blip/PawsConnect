from rest_framework import serializers

from .models import Pet, PetTransferRequest


class PetSerializer(serializers.ModelSerializer):
    pet_type = serializers.CharField()
    owner = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_transfer = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()


    def validate_pet_type(self, value):
        normalized_value = value.lower()
        choices = {choice.lower(): choice for choice, _ in Pet.PetType.choices}
        if normalized_value not in choices:
            raise serializers.ValidationError("This pet type is not allowed.")
        return choices[normalized_value]

    class Meta:
        model = Pet
        fields = ['id', 'name', 'pet_type', 'breed', 'age', 'color', 'owner', 'profile_picture_url', 'description']
        read_only_fields = ['owner']

    def get_can_edit(self, instance):
        request = self.context.get('request')
        return instance.owner == request.user

    def get_can_transfer(self, instance):
        request = self.context.get('request')
        return instance.owner == request.user

    def get_owner(self, instance):
        from UserManagement.serializers import CustomUserSerializer
        return CustomUserSerializer(instance.owner).data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if 'pet_type' in ret:
            ret['pet_type'] = instance.get_display_pet_type()
        return ret

    def get_profile_picture_url(self, obj):
        if obj.profile.profile_picture:
            return obj.profile.profile_picture.url
        return None

    def get_description(self, obj):
        return obj.profile.description


class PetTransferRequestSerializer(serializers.ModelSerializer):
    from UserManagement.models import CustomUser

    pet = serializers.PrimaryKeyRelatedField(queryset=Pet.objects.all())
    from_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    to_user = serializers.SlugRelatedField(slug_field='username', queryset=CustomUser.objects.all())
    message = serializers.CharField(required=False)
    can_accept = serializers.SerializerMethodField()
    can_reject = serializers.SerializerMethodField()

    class Meta:
        model = PetTransferRequest
        fields = ['id', 'pet', 'from_user', 'to_user', 'status', 'message']
        read_only_fields = ['from_user', 'status']

    def get_can_accept(self, instance):
        request = self.context.get('request')
        return instance.to_user == request.user  # Only recipient can accept

    def get_can_reject(self, instance):
        request = self.context.get('request')
        return instance.to_user == request.user

    def validate(self, data):
        if data['from_user'] == data['to_user']:
            raise serializers.ValidationError("You cannot create a transfer request to yourself.")
        return data


class PetTransferRequestDetailSerializer(serializers.ModelSerializer):
    pet = PetSerializer()

    class Meta:
        model = PetTransferRequest
        fields = ['id', 'pet', 'from_user', 'to_user', 'status', 'created_at', 'message']

    def get_can_cancel(self, instance):
        request = self.context.get('request')
        return instance.from_user == request.user

    def to_representation(self, instance):
        from UserManagement.serializers import CustomUserSerializer  # Import here to avoid circular dependency
        representation = super().to_representation(instance)
        representation['from_user'] = CustomUserSerializer(instance.from_user).data
        representation['to_user'] = CustomUserSerializer(instance.to_user).data
        return representation
