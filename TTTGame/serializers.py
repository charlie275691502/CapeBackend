from rest_framework import serializers
from .models import TTTBoard
from mainpage.serializers import PlayerSerializer

class TTTBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = TTTBoard
        fields = ['positions', 'turn', 'turn_of_team']
        
class TTTSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TTTSetting
        fields = ['board_size']
        
class TTTPlayerSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)

    class Meta:
        model = TTTPlayer
        fields = ['team', 'player', 'elo', 'played_game_count', 'win_game_count']

class TTTActionSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)
    action_command = TTTActionCommandSerializer(read_only=True)

    class Meta:
        model = TTTAction
        fields = ['player', 'action_command']

class TTTActionCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = TTTActionCommand
        fields = []

class TTTChoosePositionActionCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = TTTChoosePositionActionCommand
        fields = ['position']

class TTTResignActionCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = TTTResignActionCommand
        fields = []

class TTTRecordAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = TTTRecordAdmin
        fields = ['init_board', 'action_set', 'player_set', 'setting']

class TTTGameAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = TTTGameAdmin
        fields = ['board', 'player_set', 'setting']