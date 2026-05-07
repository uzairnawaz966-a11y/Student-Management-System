from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework import serializers
from django.contrib.auth.models import User
from organization.models import Membership

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, max_length=16)
    password_confirmation = serializers.CharField(write_only=True, max_length=16)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
            "password_confirmation"
        ]
        extra_kwargs = {
            "username": {"required": True},
            "email": {"required": True},
            "password": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, data):
        password = data.get("password")
        password_confirmation = data.get("password_confirmation")

        if password != password_confirmation:
            raise serializers.ValidationError("Passwords don't match")

        if User.objects.filter(email=data.get('email')).exists():
            raise serializers.ValidationError("Email already registered, Try something different.")

        if User.objects.filter(username=data.get('username')).exists():
            raise serializers.ValidationError('Username already registered, Try something different.')

        return data


class JWTLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    organization_id = serializers.IntegerField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        organization_id = data.get('organization_id')

        membership = Membership.objects.filter(
            user__username=username,
            organization_id=organization_id,
            is_active=True
        ).first()

        if not membership:
            raise serializers.ValidationError("Invalid organization")

        data["membership"] = membership

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError('User does not exist')          
        
        if not user.check_password(password):
            raise serializers.ValidationError('Invalid credentials')
        
        if not user.is_active:
            raise serializers.ValidationError('Your account is inactive. Inactive account cannot be login. We sent an activation link to your Gmail')

        data['user'] = user
        return data


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = RefreshToken(attrs["refresh"])
        organization_id = refresh.get("organization_id")
        role = refresh.get("role")

        access = AccessToken(data["access"])

        access["organization_id"] = organization_id
        access["role"] = role

        data["access"] = str(access)
        
        return data