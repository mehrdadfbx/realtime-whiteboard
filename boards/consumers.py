"""
WebSocket consumer for a whiteboard room.

Protocol (JSON messages):
  Client -> server:
    {"type": "stroke", "stroke": {"color": "#ff0000", "width": 4,
                                 "points": [{"x": 0.1, "y": 0.2}, ...]}}
    {"type": "clear"}

  Server -> client:
    {"type": "history", "strokes": [ {...}, ... ]}   # on connect
    {"type": "stroke",  "stroke": {...}}              # someone drew
    {"type": "clear"}                                # board was cleared

Broadcast goes through the Redis channel layer, so strokes reach every
connected browser even when Daphne runs multiple worker processes.
"""
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from boards.models import Room, Stroke

MAX_POINTS_PER_STROKE = 5000  # sanity cap against abusive payloads


class WhiteboardConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_slug = self.scope["url_route"]["kwargs"]["room_slug"]
        self.group_name = f"board_{self.room_slug}"

        # Reject unknown rooms instead of creating phantom groups.
        if not await self._room_exists():
            await self.close(code=4404)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # New joiner immediately sees what's already on the board.
        await self.send_json(
            {"type": "history", "strokes": await self._get_strokes()}
        )

    async def disconnect(self, close_code):
        group = getattr(self, "group_name", None)
        if group:
            await self.channel_layer.group_discard(group, self.channel_name)

    async def receive_json(self, content):
        msg_type = content.get("type")

        if msg_type == "stroke":
            stroke = await self._save_stroke(content.get("stroke") or {})
            if stroke is None:  # invalid payload -> ignore silently
                return
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "stroke_message",  # -> stroke_message() below
                    "sender": self.channel_name,
                    "stroke": stroke,
                },
            )
        elif msg_type == "clear":
            await self._clear_strokes()
            await self.channel_layer.group_send(
                self.group_name,
                {"type": "clear_message", "sender": self.channel_name},
            )

    # --- Handlers for messages arriving from the channel layer ---

    async def stroke_message(self, event):
        if event.get("sender") == self.channel_name:
            return  # don't echo the stroke back to its author
        await self.send_json({"type": "stroke", "stroke": event["stroke"]})

    async def clear_message(self, event):
        if event.get("sender") == self.channel_name:
            return
        await self.send_json({"type": "clear"})

    # --- Database access (sync ORM -> async via threadpool) ---

    @database_sync_to_async
    def _room_exists(self) -> bool:
        return Room.objects.filter(slug=self.room_slug).exists()

    @database_sync_to_async
    def _get_strokes(self) -> list:
        return [
            s.as_dict()
            for s in Stroke.objects.filter(room__slug=self.room_slug)
        ]

    @database_sync_to_async
    def _save_stroke(self, data: dict):
        """Validate, persist and return the broadcast payload (or None)."""
        color = str(data.get("color", "#111111"))[:16]
        try:
            width = max(1, min(50, int(data.get("width", 3))))
        except (TypeError, ValueError):
            return None

        points = data.get("points")
        if not isinstance(points, list) or not points:
            return None
        points = points[:MAX_POINTS_PER_STROKE]
        clean = []
        for p in points:
            try:
                x, y = float(p["x"]), float(p["y"])
            except (KeyError, TypeError, ValueError):
                return None
            # Clamp to the normalized canvas; out-of-range values are junk.
            clean.append({"x": min(1.0, max(0.0, x)),
                          "y": min(1.0, max(0.0, y))})

        stroke = Stroke.objects.create(
            room_id=self._room_id(), color=color, width=width, points=clean
        )
        return stroke.as_dict()

    @database_sync_to_async
    def _clear_strokes(self) -> None:
        Stroke.objects.filter(room__slug=self.room_slug).delete()

    def _room_id(self):
        # Called from inside _save_stroke's thread; plain ORM is fine there.
        return Room.objects.only("id").get(slug=self.room_slug).id
