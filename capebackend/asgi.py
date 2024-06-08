import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "capebackend.settings.dev")

import django
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from .channelsmiddleware import JwtAuthMiddlewareStack

django_asgi_app = get_asgi_application()

import chat.routing, TTTGame.routing, GOAGame.routing
websocket_urlpatterns = chat.routing.websocket_urlpatterns + TTTGame.routing.websocket_urlpatterns + GOAGame.routing.websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            JwtAuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)