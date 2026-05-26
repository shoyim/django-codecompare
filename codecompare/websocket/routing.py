"""Django Channels URL routing for WebSocket connections."""
from django.urls import re_path

try:
    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.auth import AuthMiddlewareStack
    from codecompare.websocket.consumers import ComparisonConsumer

    websocket_urlpatterns = [
        re_path(r"^ws/compare/(?P<room_name>\w+)/$", ComparisonConsumer.as_asgi()),
        re_path(r"^ws/compare/$", ComparisonConsumer.as_asgi()),
    ]
except ImportError:
    websocket_urlpatterns = []
