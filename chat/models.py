from django.db import models
from django.conf import settings
from mainpage.models import Player

class Room(models.Model):
    GAME_TYPE_TIC_TAC_TOE = 'TTT'
    GAME_TYPE_GENERATION_OF_AUTHORITY = 'GOA'

    GAME_TYPE_CHOICES = [
        (GAME_TYPE_TIC_TAC_TOE, 'TicTacToe'),
        (GAME_TYPE_GENERATION_OF_AUTHORITY, 'GenerationOfAuthority'),
    ]

    room_name = models.CharField(max_length=50)
    game_type = models.CharField(max_length=3, choices=GAME_TYPE_CHOICES, default=GAME_TYPE_TIC_TAC_TOE)
    create_at = models.DateTimeField(auto_now_add=True)
    players = models.ManyToManyField(Player, related_name='rooms')

    def __str__(self) -> str:
        return self.room_name

class Message(models.Model):
    content = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)
    player = models.ForeignKey(Player, on_delete=models.PROTECT, related_name='messages')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
