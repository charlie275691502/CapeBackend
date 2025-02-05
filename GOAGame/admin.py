from django.contrib import admin
from .models import GOABoard, GOAChooseOpenBoardCardActionCommand, GOAChooseRevealingBoardCardActionCommand, GOAEndCongressActionCommand, GOAEndTurnActionCommand, GOAReleaseCardsActionCommand, GOASetting, GOAPlayerSet, GOAPlayer, GOAActionSet, GOAAction, GOARecord, GOAGame, GOAActionCommand, GOARevealBoardCardsActionCommand, GOASummary, GOAUseExpandActionCommand, GOAUseMaskActionCommand, GOAUseReformActionCommand, GOAUseStrategyActionCommand

# Register your models here.

@admin.register(GOABoard)
class GOABoardAdmin(admin.ModelAdmin):
    list_display = ['draw_cards',
                    'grave_cards',
                    'strategy_cards',
                    'board_cards',
                    'open_board_card_positions',
                    'revealing_player_id',
                    'revealing_board_card_positions',
                    'turn',
                    'player_ids',
                    'taking_turn_player_id',
                    'chair_person_player_id',
                    'phase',
                    'is_last_turn']

@admin.register(GOASetting)
class GOASettingAdmin(admin.ModelAdmin):
    list_display = []

class GOAPlayerInline(admin.TabularInline):
    model = GOAPlayer

@admin.register(GOAPlayerSet)
class GOAPlayerSetAdmin(admin.ModelAdmin):
    inlines = [GOAPlayerInline]

@admin.register(GOAPlayer)
class GOAPlayerAdmin(admin.ModelAdmin):
    list_display = ['order',
                    'is_bot',
                    'character_key',
                    'public_cards',
                    'strategy_cards',
                    'power',
                    'power_limit',
                    'is_dead',
                    'is_mask_used',
                    'is_reform_used',
                    'is_expand_used',
                    'is_strategy_used',
                    'is_end_congress',
                    'player',
                    'elo', 
                    'played_game_count',
                    'win_game_count']

class GOAActionInline(admin.TabularInline):
    model = GOAAction

@admin.register(GOAActionSet)
class GOAActionSetAdmin(admin.ModelAdmin):
    inlines = [GOAActionInline]

@admin.register(GOARevealBoardCardsActionCommand)
class GOARevealBoardCardsActionCommandAdmin(admin.ModelAdmin):
    list_display = ['positions']

@admin.register(GOAChooseRevealingBoardCardActionCommand)
class GOAChooseRevealingBoardCardActionCommandAdmin(admin.ModelAdmin):
    list_display = ['position']

@admin.register(GOAChooseOpenBoardCardActionCommand)
class GOAChooseOpenBoardCardActionCommandAdmin(admin.ModelAdmin):
    list_display = ['position']
    
@admin.register(GOAUseMaskActionCommand)
class GOAUseMaskActionCommandAdmin(admin.ModelAdmin):
    list_display = ['card']
    
@admin.register(GOAUseReformActionCommand)
class GOAUseReformActionCommandAdmin(admin.ModelAdmin):
    list_display = ['card', 'target_card']
    
@admin.register(GOAUseExpandActionCommand)
class GOAUseExpandActionCommandAdmin(admin.ModelAdmin):
    list_display = ['card', 'target_position']
    
@admin.register(GOAReleaseCardsActionCommand)
class GOAReleaseCardsActionCommandAdmin(admin.ModelAdmin):
    list_display = ['cards']
    
@admin.register(GOAUseStrategyActionCommand)
class GOAUseStrategyActionCommandAdmin(admin.ModelAdmin):
    list_display = ['card', 'requirement_cards']

@admin.register(GOAEndTurnActionCommand)
class GOAEndTurnActionCommandAdmin(admin.ModelAdmin):
    list_display = []
    
@admin.register(GOAEndCongressActionCommand)
class GOAEndCongressActionCommandAdmin(admin.ModelAdmin):
    list_display = []

@admin.register(GOAAction)
class GOAActionAdmin(admin.ModelAdmin):
    list_display = ['player', 'content_type', 'object_id']

@admin.register(GOASummary)
class GOARecordAdmin(admin.ModelAdmin):
    list_display = ['winner', 'turns']
    
@admin.register(GOARecord)
class GOARecordAdmin(admin.ModelAdmin):
    list_display = ['init_board', 'action_set', 'game', 'summary']

@admin.register(GOAGame)
class GOAGameAdmin(admin.ModelAdmin):
    list_display = ['board', 'player_set', 'setting']
    