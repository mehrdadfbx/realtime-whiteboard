from django.shortcuts import get_object_or_404, redirect, render

from boards.models import Room


def index(request):
    """Landing page: mint a fresh room and send the user to it."""
    room = Room.objects.create()
    return redirect("boards:board", slug=room.slug)


def board(request, slug):
    """Render the whiteboard page for an existing room."""
    room = get_object_or_404(Room, slug=slug)
    return render(request, "boards/board.html", {"room": room})
