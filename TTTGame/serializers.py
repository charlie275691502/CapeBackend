from rest_framework import serializers
from .models import TTTBoard, TTTSetting, TTTPlayer, TTTAction, TTTActionCommand, TTTChoosePositionActionCommand, TTTResignActionCommand, TTTRecord, TTTGame
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

class TTTActionCommandSerializer(serializers.Serializer):
    class Meta:
        model = TTTActionCommand
        abstract = True
        fields = []

class TTTChoosePositionActionCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = TTTChoosePositionActionCommand
        fields = ['position']

class TTTResignActionCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = TTTResignActionCommand
        fields = []

class TTTActionSerializer(serializers.ModelSerializer):
    player_id = serializers.SerializerMethodField(method_name='get_player_id')
    action_command_type = serializers.SerializerMethodField(method_name='get_action_command_type')
    action_command = serializers.SerializerMethodField(method_name='get_action_command')

    class Meta:
        model = TTTAction
        fields = ['player_id', 'action_command_type', 'action_command']

    def get_player_id(self, action: TTTAction):
        return action.player.player.user.id
    
    def get_action_command_type(self, action: TTTAction):
        action_command_type_str = str(type(action.action_command))
        return action_command_type_str.split('.')[-1][3:-15]

    def get_action_command(self, action: TTTAction):
        action_command_type = type(action.action_command)

        if action_command_type is TTTChoosePositionActionCommand:
            return TTTChoosePositionActionCommandSerializer(action.action_command).data
        if action_command_type is TTTResignActionCommand:
            return TTTResignActionCommandSerializer(action.action_command).data
        return TTTActionCommandSerializer(action.action_command).data

class TTTRecordSerializer(serializers.ModelSerializer):
    init_board = TTTBoardSerializer(read_only=True)
    actions = serializers.SerializerMethodField(method_name='get_actions')
    players = serializers.SerializerMethodField(method_name='get_players')
    setting = TTTSettingSerializer(read_only=True)

    class Meta:
        model = TTTRecord
        fields = ['init_board', 'actions', 'players', 'setting']

    def get_actions(self, record: TTTRecord):
        return TTTActionSerializer(record.action_set.actions.all(), many = True).data

    def get_players(self, record: TTTRecord):
        return TTTPlayerSerializer(record.player_set.players.all(), many = True).data

class TTTGameSerializer(serializers.ModelSerializer):
    board = TTTBoardSerializer(read_only=True)
    players = serializers.SerializerMethodField(method_name='get_players')
    setting = TTTSettingSerializer(read_only=True)
    
    class Meta:
        model = TTTGame
        fields = ['id', 'board', 'players', 'setting']

    def get_players(self, game: TTTGame):
        return TTTPlayerSerializer(game.player_set.players.all(), many = True).data