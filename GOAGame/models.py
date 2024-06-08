from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from mainpage.models import Player

class GOABoard(models.Model):
    draw_card_count = models.IntegerField(default=0)
    grave_card_count = models.IntegerField(default=0)
    cards = ArrayField(models.PositiveSmallIntegerField(default=-1), null=True, blank=True)
    turn = models.IntegerField(default=1)
    taking_turn_player_id = models.IntegerField(default=0)

class GOASetting(models.Model):
    pass

class GOAPlayerSet(models.Model):
    pass

class GOAPlayer(models.Model):
    order = models.IntegerField(default=0)
    is_bot = models.BooleanField(default=False)
    character_key = models.CharField(max_length=50)
    public_cards = ArrayField(models.PositiveSmallIntegerField(default=-1), null=True, blank=True)
    public_card_count = models.IntegerField(default=0)
    strategy_cards = ArrayField(models.PositiveSmallIntegerField(default=-1), null=True, blank=True)
    strategy_card_count = models.IntegerField(default=0)
    power = models.IntegerField(default=0)
    power_limit = models.IntegerField(default=0)
    
    player = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL)
    elo = models.IntegerField(default=0)
    played_game_count = models.IntegerField(default=0)
    win_game_count = models.IntegerField(default=0)
    player_set = models.ForeignKey(GOAPlayerSet, on_delete=models.CASCADE, related_name='players')

class GOAActionCommand(models.Model):
    class Meta:
        abstract = True

class GOARevealBoardCardsActionCommand(GOAActionCommand):
    positions = ArrayField(models.PositiveSmallIntegerField(default=0), null=True, blank=True)
    pass

class GOAChooseBoardCardActionCommand(GOAActionCommand):
    position = models.IntegerField(default=0)
    pass

class GOAActionSet(models.Model):
    pass

class GOAAction(models.Model):
    action_set = models.ForeignKey(GOAActionSet, on_delete=models.CASCADE, related_name='actions')
    player = models.ForeignKey(GOAPlayer, null=True, blank=True, on_delete=models.SET_NULL)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    action_command = GenericForeignKey('content_type', 'object_id')

class GOAGame(models.Model):
    board = models.OneToOneField(GOABoard, on_delete=models.PROTECT)
    player_set = models.OneToOneField(GOAPlayerSet, on_delete=models.PROTECT)
    setting = models.OneToOneField(GOASetting, on_delete=models.PROTECT)

class GOASummary(models.Model):
    winner = models.ForeignKey(GOAPlayer, null=True, blank=True, on_delete=models.SET_NULL)
    turns = models.IntegerField(default=1)
    
class GOARecord(models.Model):
    init_board = models.OneToOneField(GOABoard, on_delete=models.PROTECT)
    action_set = models.OneToOneField(GOAActionSet, on_delete=models.PROTECT)
    game = models.OneToOneField(GOAGame, on_delete=models.PROTECT)
    summary = models.OneToOneField(GOASummary, null=True, blank=True, on_delete=models.PROTECT)
    