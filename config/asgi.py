"""ASGI entry point — supports HTTP and WebSocket."""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

import django
django.setup()

try:
    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.auth import AuthMiddlewareStack
    from django.core.asgi import get_asgi_application
    from codecompare.websocket.routing import websocket_urlpatterns

    application = ProtocolTypeRouter({
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    })
except ImportError:
    from django.core.asgi import get_asgi_application
    application = get_asgi_application()
