from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Кастомный сериализатор для получения токена по email"""

    username_field = "email"

    def validate(self, attrs):

        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )

        if user is None:
            raise serializers.ValidationError("Неверный email или пароль")

        if not user.is_active:
            raise serializers.ValidationError("Учетная запись неактивна")

        data = super().validate(attrs)

        data.update(
            {
                "user_id": user.id,
                "email": user.email,
            }
        )

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token


class UserSerializer(ModelSerializer):
    """Сериализатор для пользователя"""

    password = serializers.CharField(write_only=True, required=True)
    last_login = serializers.DateTimeField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "phone_number",
            "city",
            "avatar",
            "is_active",
            "last_login",
            "date_joined",
        ]
        read_only_fields = ["id", "is_active"]

    def create(self, validated_data):
        """Создание пользователя с хешированием пароля"""

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            phone_number=validated_data.get("phone_number"),
            city=validated_data.get("city"),
            avatar=validated_data.get("avatar"),
        )
        return user


class UserRetrieveSerializer(ModelSerializer):
    """Сериализатор для получения информации о пользователе"""

    last_login = serializers.DateTimeField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone_number",
            "city",
            "avatar",
            "is_active",
            "last_login",
            "date_joined",
        ]
        read_only_fields = ["id", "email", "is_active"]


class UserUpdateSerializer(ModelSerializer):
    """Сериализатор для обновления пользователя"""

    class Meta:
        model = User
        fields = ["phone_number", "city", "avatar"]

    def update(self, instance, validated_data):
        """Обновление только разрешенных полей"""
        instance.phone_number = validated_data.get(
            "phone_number", instance.phone_number
        )
        instance.city = validated_data.get("city", instance.city)
        instance.avatar = validated_data.get("avatar", instance.avatar)
        instance.save()
        return instance
