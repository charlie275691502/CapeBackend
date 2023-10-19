from django.contrib import admin
from .models import Room, Message

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_name', 'game_type']
    pass

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['content']
