"""
ASGI entry point.

ProtocolTypeRouter splits traffic by protocol:
  - "http"     -> normal Django request handling
  - "websocket" -> Channels consumers (the whiteboard realtime layer)

AllowedHostsOriginValidator rejects WebSocket handshakes whose Origin
header doesn't match ALLOWED_HOSTS (basic CSWSH protection).
"""
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "whiteboard_project.settings")

# Initialize Django before importing anything that touches models.
django_asgi_app = get_asgi_application()

from boards import routing  # noqa: E402  (import after Django setup)

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))
        ),
    }
)
