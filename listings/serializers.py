from rest_framework import serializers, request
from django.contrib.auth import get_user_model,authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role')

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data['role']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'username'

    def validate(self, attrs):
        username = attrs.get(self.username_field)
        password = attrs.get("password")

        if username and password:
            user = authenticate(
                request=self.context.get("request"),
                **{self.username_field: username, "password": password}
            )
            if not user:
                raise serializers.ValidationError(
                    _("No active account found with the given credentials"),
                    code="authorization",
                )

        else:
            raise serializers.ValidationError(
                _("Must include '%s' and 'password'.") % self.username_field,
                code="authorization",
            )

        refresh = self.get_token(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            },
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']


