from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "phone", "first_name", "last_name", "role", "is_active")

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = User
        fields = ("email", "phone", "password", "first_name", "last_name")

    def validate(self, data):
        if not data.get("email") and not data.get("phone"):
            raise serializers.ValidationError("Provide email or phone.")
        return data

    def create(self, validated_data):
        pwd = validated_data.pop("password")
        user = User.objects.create_user(password=pwd, **validated_data)
        user.is_active = False
        user.save()
        return user

# class ProfileSerializer(serializers.ModelSerializer):
#     user = UserSerializer(read_only=True)
#     class Meta:
#         model = Profile
#         fields = ("user", "address", "avatar", "extra")


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ["user", "address", "avatar", "extra"]

    def update(self, instance, validated_data):
        # Extract user data if present
        user_data = validated_data.pop("user", None)

        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update nested user fields
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        return instance




class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        # You can add Django's built-in password validators here
        from django.contrib.auth.password_validation import validate_password
        validate_password(value)
        return value

