from django.urls import re_path

from .consumers import GOAGameConsumer

websocket_urlpatterns = [
    re_path(r"ws/GOAGame/games/(?P<game_id>\w+)/$", GOAGameConsumer.as_asgi()),
]