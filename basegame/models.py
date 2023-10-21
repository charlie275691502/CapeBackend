from django.db import models

class BaseGameSetting(models.Model):
    GAME_TYPE_NONE = 'NON'
    GAME_TYPE_TIC_TAC_TOE = 'TTT'
    GAME_TYPE_GENERATION_OF_AUTHORITY = 'GOA'

    GAME_TYPE_CHOICES = [
        (GAME_TYPE_NONE, 'NONE'),
        (GAME_TYPE_TIC_TAC_TOE, 'TicTacToe'),
        (GAME_TYPE_GENERATION_OF_AUTHORITY, 'GenerationOfAuthority'),
    ]

    game_type = models.CharField(max_length=3, choices=GAME_TYPE_CHOICES, default=GAME_TYPE_NONE)
    player_limit = models.IntegerField(null=True, blank=True, default=1)

    def default():
        default = BaseGameSetting()
        default.save()
        return default.pk