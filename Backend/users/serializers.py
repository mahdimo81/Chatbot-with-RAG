import re
from .models import CustomUser
from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.hashers import make_password


import pytz
from django.utils.timezone import now
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



def is_strong_password(password):
    # Returns True if the password meets security requirements, otherwise False.
    return (
        len(password) >= 8
        and any(char.isupper() for char in password)
        and any(char.islower() for char in password)
        and any(char.isdigit() for char in password)
        and re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    )


class CustomUserSerializer(serializers.ModelSerializer):
    # DRF does not require us to write all validation conditions because it checks conditions from models.py
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "last_login",
            "date_joined",
            "password",
        ]
        extra_kwargs = {
            "last_login": {"read_only": True},
            "date_joined": {"read_only": True},
            "password": {"write_only": True},
        }

    def validate_password(self, value):
        if not is_strong_password(value):
            raise serializers.ValidationError(
                "Weak password. Must contain at least 8 characters, one uppercase, "
                "one lowercase, one digit, and one special character."
            )
        return value

    def create(self, validated_data):
        # Hash the password before saving the user
        password = validated_data.pop(
            "password", None
        )  # Remove password from validated_data
        validated_data["username"] = validated_data["username"].lower()
        validated_data["password"] = make_password(password)  # Hash the password

        return CustomUser.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            password = validated_data.pop(
                "password", None
            )  # Remove password from validated_data
            validated_data["password"] = make_password(password)  # Hash the password

        if "username" in validated_data:
            validated_data["username"] = validated_data["username"].lower()

        validated_data.pop("id", None)  # Prevent id updates
        return super().update(instance, validated_data)



class CustomTokenObtainPairSerializer(
    TokenObtainPairSerializer
):  # Custom serializer for JWT authentication
    def validate(self, attrs):  # Validate user credentials
        try:
            data = super().validate(attrs)  # Call parent class validation
        except Exception:
            raise AuthenticationFailed("Invalid credentials")  # Raise error on failure

        user = self.user  # Get authenticated user

        # Update last login timestamp and user token_invalidated
        tehran_tz = pytz.timezone("Asia/Tehran")
        user.last_login = now().astimezone(tehran_tz)
        user.token_invalidated = False  # Invalidate authentication token
        user.save(update_fields=["last_login", "token_invalidated"])

        # Add user details into response
        data.update(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "last_login": user.last_login,
                }
            }
        )

        return data