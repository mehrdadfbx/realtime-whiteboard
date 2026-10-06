from django.urls import path

from boards import views

app_name = "boards"

urlpatterns = [
    path("", views.index, name="index"),          # creates a room, redirects
    path("<slug:slug>/", views.board, name="board"),
]
