from django.urls import re_path

from .consumers import ChatConsumer, RoomManageConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/rooms/(?P<room_id>\w+)/$", ChatConsumer.as_asgi()),
    re_path(r"ws/chat/room_manage/$", RoomManageConsumer.as_asgi()),
]