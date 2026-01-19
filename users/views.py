from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from users.models import User
from users.serializers import (
    UserSerializer,
    CustomTokenObtainPairSerializer,
    UserUpdateSerializer,
    UserRetrieveSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для пользователей с полным CRUD"""

    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return UserSerializer
        elif self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return UserRetrieveSerializer

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        elif self.action in ["update", "partial_update", "destroy", "retrieve"]:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name="moderators").exists():
            return User.objects.all()
        return User.objects.filter(id=user.id)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Кастомное представление для получения токенов по email"""

    serializer_class = CustomTokenObtainPairSerializer
