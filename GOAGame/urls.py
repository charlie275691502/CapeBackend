from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GOARecordViewSet, GOAGameViewSet

router = DefaultRouter()
router.register('record', GOARecordViewSet, basename = 'record')
router.register('game', GOAGameViewSet, basename = 'game')

urlpatterns = [
    path('', include(router.urls)),
]