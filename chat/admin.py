from django.contrib import admin
from .models import Room, Message

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_name', 'game_type']

    def game_type(self, room):
        return room.game_setting.game_type

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['content']
