from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import HabitViewSet, PublicHabitListAPIView

app_name = 'habit'

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habit')

urlpatterns = [
    path('', include(router.urls)),
    path('public-habits/', PublicHabitListAPIView.as_view(), name='public-habits'),
]
