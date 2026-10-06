import uuid

from django.db import models


def new_room_slug() -> str:
    """Short, unguessable room identifier used in share links."""
    return uuid.uuid4().hex[:8]


class Room(models.Model):
    """A single collaborative whiteboard. Shared via /<slug>/."""

    name = models.CharField(max_length=120, default="Whiteboard")
    slug = models.SlugField(max_length=16, unique=True, default=new_room_slug)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} ({self.slug})"


class Stroke(models.Model):
    """
    One pen stroke on a board.

    Points are stored normalized (0.0–1.0 relative to canvas size) so a
    stroke drawn on a phone renders correctly on a desktop and vice versa.
    Example: [{"x": 0.12, "y": 0.34}, {"x": 0.15, "y": 0.36}]
    """

    room = models.ForeignKey(Room, related_name="strokes", on_delete=models.CASCADE)
    color = models.CharField(max_length=16, default="#111111")
    width = models.PositiveSmallIntegerField(default=3)
    points = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"Stroke {self.id} in {self.room.slug}"

    def as_dict(self) -> dict:
        """JSON-safe payload broadcast to WebSocket clients."""
        return {
            "id": self.id,
            "color": self.color,
            "width": self.width,
            "points": self.points,
        }
