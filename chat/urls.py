from django.urls import path, include
from rest_framework_nested import routers
from .views import RoomViewSet, MessageViewSet

router = routers.DefaultRouter()
router.register('rooms', RoomViewSet, basename = 'rooms')

rooms_router = routers.NestedDefaultRouter(router, 'rooms', lookup='room')
rooms_router.register('messages', MessageViewSet, basename='messages-detail')

urlpatterns = router.urls + rooms_router.urls