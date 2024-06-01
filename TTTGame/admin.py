from django.contrib import admin
from .models import TTTBoard, TTTSetting, TTTPlayerSet, TTTPlayer, TTTActionSet, TTTAction, TTTRecord, TTTGame, TTTActionCommand, TTTChoosePositionActionCommand, TTTResignActionCommand

# Register your models here.

@admin.register(TTTBoard)
class TTTBoardAdmin(admin.ModelAdmin):
    list_display = ['positions', 'turn', 'turn_of_team']

@admin.register(TTTSetting)
class TTTSettingAdmin(admin.ModelAdmin):
    list_display = ['board_size']

class TTTPlayerInline(admin.TabularInline):
    model = TTTPlayer

@admin.register(TTTPlayerSet)
class TTTPlayerSetAdmin(admin.ModelAdmin):
    inlines = [TTTPlayerInline]

@admin.register(TTTPlayer)
class TTTPlayerAdmin(admin.ModelAdmin):
    list_display = ['team', 'player', 'elo', 'played_game_count', 'win_game_count']

class TTTActionInline(admin.TabularInline):
    model = TTTAction

@admin.register(TTTActionSet)
class TTTActionSetAdmin(admin.ModelAdmin):
    inlines = [TTTActionInline]

@admin.register(TTTChoosePositionActionCommand)
class TTTChoosePositionActionCommandAdmin(admin.ModelAdmin):
    list_display = ['position']

@admin.register(TTTResignActionCommand)
class TTTResignActionCommandAdmin(admin.ModelAdmin):
    pass

@admin.register(TTTAction)
class TTTActionAdmin(admin.ModelAdmin):
    list_display = ['player', 'content_type', 'object_id']

@admin.register(TTTRecord)
class TTTRecordAdmin(admin.ModelAdmin):
    list_display = ['init_board', 'action_set', 'game']

@admin.register(TTTGame)
class TTTGameAdmin(admin.ModelAdmin):
    list_display = ['board', 'player_set', 'setting']
    