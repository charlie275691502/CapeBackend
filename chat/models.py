from django.db import models
from django.conf import settings
from mainpage.models import Player
from basegame.models import BaseGameSetting

class Room(models.Model):
    room_name = models.CharField(max_length=50)
    game_setting = models.OneToOneField(BaseGameSetting, on_delete=models.PROTECT, default=BaseGameSetting.default)
    create_at = models.DateTimeField(auto_now_add=True)
    players = models.ManyToManyField(Player, related_name='rooms')

    def __str__(self) -> str:
        return self.room_name

class Message(models.Model):
    content = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)
    player = models.ForeignKey(Player, on_delete=models.PROTECT, related_name='messages')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
