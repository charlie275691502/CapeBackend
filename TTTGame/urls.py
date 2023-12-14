from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlayerViewSet

router = DefaultRouter()
router.register('record', TTTRecordViewSet, basename = 'record')
router.register('game', TTTGameViewSet, basename = 'game')

urlpatterns = [
    path('', include(router.urls)),
]