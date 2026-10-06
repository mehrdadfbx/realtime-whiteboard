from django.urls import re_path

from boards import consumers

# ws/boards/<8-hex-chars>/  e.g. ws/boards/9f3ac2e1/
websocket_urlpatterns = [
    re_path(
        r"ws/boards/(?P<room_slug>[0-9a-f]{8})/$",
        consumers.WhiteboardConsumer.as_asgi(),
    ),
]
