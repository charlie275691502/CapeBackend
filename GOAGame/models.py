from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from mainpage.models import Player

class GOABoard(models.Model):
    draw_cards = ArrayField(models.PositiveSmallIntegerField(default=-1), null=True, blank=True)
    grave_cards = ArrayField(models.PositiveSmallIntegerField(default=-1), null=True, blank=True)
    strategy_cards = ArrayField(models.PositiveSmallIntegerField(default=-1), null=True, blank=True)
    board_cards = ArrayField(models.PositiveSmallIntegerField(default=-1), null=True, blank=True)
    open_board_card_positions = ArrayField(models.PositiveSmallIntegerField(default=0), null=True, blank=True)
    revealing_player_id = models.IntegerField(default=0)
    revealing_board_card_positions = ArrayField(models.PositiveSmallIntegerField(default=0), null=True, blank=True)
    turn = models.IntegerField(default=1)
    player_ids = ArrayField(models.PositiveSmallIntegerField(default=0), null=True, blank=True)
    taking_turn_player_id = models.IntegerField(default=0)
    chair_person_player_id = models.IntegerField(default=0)
    phase = models.IntegerField(default=0)
    is_last_turn = models.BooleanField(default=0)

class GOASetting(models.Model):
    pass

class GOAPlayerSet(models.Model):
    pass

class GOAPlayer(models.Model):
    order = models.IntegerField(default=0)
    is_bot = models.BooleanField(default=False)
    character_key = models.CharField(max_length=50)
    public_cards = ArrayField(models.PositiveSmallIntegerField(default=-1), null=True, blank=True)
    strategy_cards = ArrayField(models.PositiveSmallIntegerField(default=-1), null=True, blank=True)
    power = models.IntegerField(default=0)
    power_limit = models.IntegerField(default=0)
    is_dead = models.BooleanField(default=False)
    is_mask_used = models.BooleanField(default=False)
    is_reform_used = models.BooleanField(default=False)
    is_expand_used = models.BooleanField(default=False)
    is_strategy_used = models.BooleanField(default=False)
    is_end_congress = models.BooleanField(default=False)
    
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

class GOAChooseRevealingBoardCardActionCommand(GOAActionCommand):
    position = models.IntegerField(default=0)
    pass

class GOAChooseOpenBoardCardActionCommand(GOAActionCommand):
    position = models.IntegerField(default=0)
    pass

class GOAUseMaskActionCommand(GOAActionCommand):
    card = models.IntegerField(default=0)
    pass

class GOAUseReformActionCommand(GOAActionCommand):
    card = models.IntegerField(default=0)
    target_card = models.IntegerField(default=0)
    pass

class GOAUseExpandActionCommand(GOAActionCommand):
    card = models.IntegerField(default=0)
    target_position = models.IntegerField(default=0)
    pass

class GOAReleaseCardsActionCommand(GOAActionCommand):
    cards = ArrayField(models.PositiveSmallIntegerField(default=0), null=True, blank=True)
    pass

class GOAUseStrategyActionCommand(GOAActionCommand):
    card = models.IntegerField(default=0)
    requirement_cards = ArrayField(models.PositiveSmallIntegerField(default=0), null=True, blank=True)
    pass

class GOAEndTurnActionCommand(GOAActionCommand):
    pass

class GOAEndCongressActionCommand(GOAActionCommand):
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
    