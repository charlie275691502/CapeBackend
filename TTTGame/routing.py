from django.urls import re_path

from .consumers import TTTGameConsumer

websocket_urlpatterns = [
    re_path(r"ws/TTTGame/games/(?P<game_id>\w+)/$", TTTGameConsumer.as_asgi()),
]