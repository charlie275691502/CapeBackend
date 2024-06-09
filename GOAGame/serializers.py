from rest_framework import serializers
from .models import GOABoard, GOASetting, GOAPlayer, GOAAction, GOAActionCommand, GOARevealBoardCardsActionCommand, GOAChooseBoardCardActionCommand, GOARecord, GOAGame, GOASummary
from mainpage.serializers import PlayerSerializer

class GOABoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = GOABoard
        fields = ['draw_card_count',
                  'grave_card_count',
                  'cards',
                  'open_card_positions',
                  'revealing_player_id',
                  'revealing_card_positions',
                  'turn',
                  'taking_turn_player_id']
        
class GOASettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GOASetting
        fields = []
        
class GOAPlayerSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)

    class Meta:
        model = GOAPlayer
        fields = ['order',
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

class GOAActionCommandSerializer(serializers.Serializer):
    class Meta:
        model = GOAActionCommand
        abstract = True
        fields = []

class GOARevealBoardCardsActionCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GOARevealBoardCardsActionCommand
        fields = ['positions']

class GOAChooseBoardCardActionCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GOAChooseBoardCardActionCommand
        fields = ['position']

class GOAActionSerializer(serializers.ModelSerializer):
    player_id = serializers.SerializerMethodField(method_name='get_player_id')
    action_command_type = serializers.SerializerMethodField(method_name='get_action_command_type')
    action_command = serializers.SerializerMethodField(method_name='get_action_command')

    class Meta:
        model = GOAAction
        fields = ['player_id', 'action_command_type', 'action_command']

    def get_player_id(self, action: GOAAction):
        return action.player.player.user.id
    
    def get_action_command_type(self, action: GOAAction):
        action_command_type_str = str(type(action.action_command))
        return action_command_type_str.split('.')[-1][3:-15]

    def get_action_command(self, action: GOAAction):
        action_command_type = type(action.action_command)

        if action_command_type is GOARevealBoardCardsActionCommand:
            return GOARevealBoardCardsActionCommandSerializer(action.action_command).data
        if action_command_type is GOAChooseBoardCardActionCommand:
            return GOAChooseBoardCardActionCommandSerializer(action.action_command).data
        return GOAActionCommandSerializer(action.action_command).data

class GOASummarySerializer(serializers.ModelSerializer):
    winner = GOAPlayerSerializer(read_only=True)
    
    class Meta:
        model = GOASummary
        fields = ['winner', 'turns']
    
class GOARecordSerializer(serializers.ModelSerializer):
    init_board = GOABoardSerializer(read_only=True)
    actions = serializers.SerializerMethodField(method_name='get_actions')
    players = serializers.SerializerMethodField(method_name='get_players')
    setting = GOASettingSerializer(read_only=True)
    summary = GOASummarySerializer(read_only=True)

    class Meta:
        model = GOARecord
        fields = ['init_board', 'actions', 'players', 'setting', 'summary']

    def get_actions(self, record: GOARecord):
        return GOAActionSerializer(record.action_set.actions.all(), many = True).data

    def get_players(self, record: GOARecord):
        return GOAPlayerSerializer(record.player_set.players.all(), many = True).data

class GOAGameSerializer(serializers.ModelSerializer):
    board = GOABoardSerializer(read_only=True)
    players = serializers.SerializerMethodField(method_name='get_players')
    setting = GOASettingSerializer(read_only=True)
    
    class Meta:
        model = GOAGame
        fields = ['id', 'board', 'players', 'setting']

    def get_players(self, game: GOAGame):
        return GOAPlayerSerializer(game.player_set.players.all(), many = True).data