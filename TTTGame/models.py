from django.db import models
from django.contrib.postgres.fields import ArrayField
from mainpage.models import Player


class TTTBoard(models.Model):
    positions = ArrayField(models.PositiveSmallIntegerField(default=0), null=True, blank=True)
    turn = models.IntegerField(default=0)
    turn_of_team = models.IntegerField(default=0)

class TTTSetting(models.Model):
    board_size = models.IntegerField(default=0)

class TTTPlayerSet(models.Model):
    pass

class TTTPlayer(models.Model):
    team = models.IntegerField(default=0)
    user = models.OneToOneField(Player, null=True, blank=True, on_delete=models.SET_NULL)
    elo = models.IntegerField(default=0)
    played_game_count = models.IntegerField(default=0)
    win_game_count = models.IntegerField(default=0)
    player_set = models.ForeignKey(TTTPlayerSet, on_delete=models.CASCADE, related_name='players')

class TTTActionSet(models.Model):
    pass

class TTTAction(models.Model):
    action_set = models.ForeignKey(TTTActionSet, on_delete=models.CASCADE, related_name='actions')


class TTTRecord(models.Model):
    init_board = models.OneToOneField(TTTBoard, on_delete=models.PROTECT)
    action_set = models.OneToOneField(TTTActionSet, on_delete=models.PROTECT)
    player_set = models.OneToOneField(TTTPlayerSet, on_delete=models.PROTECT)
    setting = models.OneToOneField(TTTSetting, on_delete=models.PROTECT)

class TTTGame(models.Model):
    board = models.OneToOneField(TTTBoard, on_delete=models.PROTECT)
    action_set = models.OneToOneField(TTTActionSet, on_delete=models.PROTECT)
    player_set = models.OneToOneField(TTTPlayerSet, on_delete=models.PROTECT)
    setting = models.OneToOneField(TTTSetting, on_delete=models.PROTECT)