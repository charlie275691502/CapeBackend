from django.contrib import admin
from .models import GOABoard, GOAChooseOpenBoardCardActionCommand, GOAChooseRevealingBoardCardActionCommand, GOASetting, GOAPlayerSet, GOAPlayer, GOAActionSet, GOAAction, GOARecord, GOAGame, GOAActionCommand, GOARevealBoardCardsActionCommand, GOASummary

# Register your models here.

@admin.register(GOABoard)
class GOABoardAdmin(admin.ModelAdmin):
    list_display = ['draw_cards',
                    'grave_cards',
                    'board_cards',
                    'open_board_card_positions',
                    'revealing_player_id',
                    'revealing_board_card_positions',
                    'turn',
                    'player_ids',
                    'taking_turn_player_id',
                    'phase']

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
                    'public_card_count',
                    'strategy_cards',
                    'strategy_card_count',
                    'power',
                    'power_limit',
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
    