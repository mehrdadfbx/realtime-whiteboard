from django.contrib import admin

from boards.models import Room, Stroke


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    readonly_fields = ("slug", "created_at")


@admin.register(Stroke)
class StrokeAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "color", "width", "created_at")
    list_filter = ("room",)
