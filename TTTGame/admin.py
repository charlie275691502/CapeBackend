from django.contrib import admin
from .models import TTTBoard, TTTSetting, TTTPlayerSet, TTTPlayer, TTTActionSet, TTTAction, TTTRecord, TTTGame

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
    inlines = [
        TTTPlayerInline,
    ]

@admin.register(TTTPlayer)
class TTTPlayerAdmin(admin.ModelAdmin):
    list_display = ['team', 'elo', 'played_game_count', 'win_game_count']

# @admin.register(TTTActionSet)
# class TTTActionSetAdmin(admin.ModelAdmin):

# @admin.register(TTTAction)
# class TTTActionAdmin(admin.ModelAdmin):

# @admin.register(TTTRecord)
# class TTTRecordAdmin(admin.ModelAdmin):

# @admin.register(TTTGame)
# class TTTGameAdmin(admin.ModelAdmin):
    