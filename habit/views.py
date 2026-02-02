from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Habit
from .pagination import HabitPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import HabitSerializer, PublicHabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с привычками пользователя"""

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = HabitPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_pleasant", "is_public"]

    def get_queryset(self):
        """Возвращает только привычки текущего пользователя"""
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Автоматически привязываем текущего пользователя к создаваемой привычке"""
        serializer.save(user=self.request.user)


class PublicHabitListAPIView(generics.ListAPIView):
    """API эндпоинт для получения списка публичных привычек"""

    serializer_class = PublicHabitSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = HabitPagination

    def get_queryset(self):
        """Возвращает публичные привычки, исключая привычки текущего пользователя"""
        return Habit.objects.filter(is_public=True).exclude(user=self.request.user)
