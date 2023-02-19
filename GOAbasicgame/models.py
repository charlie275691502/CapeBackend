from django.db import models
from django.contrib.postgres.fields import ArrayField
from core.models import User

class GOABasicGameAction(models.Model):
    player_id = models.IntegerField(null=True, blank=True)
    action_id = models.IntegerField(null=True, blank=True)
    action_parameter = models.IntegerField(null=True, blank=True)

class GOABasicGameProfile(models.Model):
    elo = models.IntegerField(null=True, blank=True)
    played_game_count = models.IntegerField(null=True, blank=True)
    win_game_count = models.IntegerField(null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='goa_basic_game_profile')

class GOABasicBoardStatus(models.Model):
    draw_pile_card_ids = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    deck_card_ids = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    deck_card_revealed = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    deck_card_seen_by_player_id = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    player_card_ids = ArrayField(ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True), null=True, blank=True)
    current_player_id = models.IntegerField(null=True, blank=True)
    current_turn = models.IntegerField(null=True, blank=True)

class GOABasicGameStatus(models.Model):
    board_statuses = GOABasicBoardStatus()
    player_ids = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    random_seed = models.IntegerField(null=True, blank=True)

class GOABasicGameRecord(models.Model):
    player_ids = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    random_seed = models.IntegerField(null=True, blank=True)
    game_status = models.OneToOneField(GOABasicGameStatus, on_delete=models.DO_NOTHING)
    actions = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
