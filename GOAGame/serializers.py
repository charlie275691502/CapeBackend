from rest_framework import serializers
from .models import GOABoard, GOAChooseOpenBoardCardActionCommand, GOAChooseRevealingBoardCardActionCommand, GOAEndCongressActionCommand, GOAEndTurnActionCommand, GOAReleaseCardsActionCommand, GOASetting, GOAPlayer, GOAAction, GOAActionCommand, GOARevealBoardCardsActionCommand, GOARecord, GOAGame, GOASummary, GOAUseExpandActionCommand, GOAUseMaskActionCommand, GOAUseReformActionCommand, GOAUseStrategyActionCommand
from mainpage.serializers import PlayerSerializer

class GOABoardSerializer(serializers.ModelSerializer):
    draw_card_count = serializers.SerializerMethodField(method_name='get_draw_card_count')
    grave_card_count = serializers.SerializerMethodField(method_name='get_grave_card_count')
    masked_board_cards = serializers.SerializerMethodField(method_name='get_masked_board_cards')
    
    class Meta:
        model = GOABoard
        fields = ['draw_card_count',
                  'grave_card_count',
                  'masked_board_cards',
                  'revealing_board_card_positions',
                  'turn',
                  'taking_turn_player_id',
                  'phase']
        
    def get_draw_card_count(self, board: GOABoard):
        return len(board.draw_cards)
        
    def get_grave_card_count(self, board: GOABoard):
        return len(board.grave_cards)
        
    def get_masked_board_cards(self, board: GOABoard):
        return [board_card if board_card == -1 or position in board.open_board_card_positions else 0
                for (position, board_card) in enumerate(board.board_cards)]
        
class GOABoardRevealingSerializer(serializers.ModelSerializer):
    draw_card_count = serializers.SerializerMethodField(method_name='get_draw_card_count')
    grave_card_count = serializers.SerializerMethodField(method_name='get_grave_card_count')
    masked_board_cards = serializers.SerializerMethodField(method_name='get_masked_board_cards')
    
    class Meta:
        model = GOABoard
        fields = ['draw_card_count',
                  'grave_card_count',
                  'masked_board_cards',
                  'revealing_board_card_positions',
                  'turn',
                  'taking_turn_player_id',
                  'chair_person_player_id',
                  'phase',
                  'is_last_turn']
        
    def get_draw_card_count(self, board: GOABoard):
        return len(board.draw_cards)
        
    def get_grave_card_count(self, board: GOABoard):
        return len(board.grave_cards)
        
    def get_masked_board_cards(self, board: GOABoard):
        return [board_card if board_card == -1 or position in board.open_board_card_positions or position in board.revealing_board_card_positions else 0
                for (position, board_card) in enumerate(board.board_cards)]
        
class GOASettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GOASetting
        fields = []
        
class GOAPlayerSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)
    public_card_count = serializers.SerializerMethodField(method_name='get_public_card_count')
    strategy_card_count = serializers.SerializerMethodField(method_name='get_strategy_card_count')

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
        
    def get_public_card_count(self, player: GOAPlayer):
        return len(player.public_cards)
        
    def get_strategy_card_count(self, player: GOAPlayer):
        return len(player.strategy_cards)

class GOAActionCommandSerializer(serializers.Serializer):
    class Meta:
        model = GOAActionCommand
        abstract = True
        fields = []

class GOARevealBoardCardsActionCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GOARevealBoardCardsActionCommand
        fields = ['positions']

class GOAChooseRevealingBoardCardActionCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GOAChooseRevealingBoardCardActionCommand
        fields = ['position']

class GOAChooseOpenBoardCardActionCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GOAChooseOpenBoardCardActionCommand
        fields = ['position']

class GOAUseMaskActionCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GOAUseMaskActionCommand
        fields = ['card']

class GOAUseReformActionCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GOAUseReformActionCommand
        fields = ['card', 'target_card']

class GOAUseExpandActionCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GOAUseExpandActionCommand
        fields = ['card', 'target_position']

class GOAReleaseCardsActionCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GOAReleaseCardsActionCommand
        fields = ['cards']

class GOAUseStrategyActionCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GOAUseStrategyActionCommand
        fields = ['card', 'requirement_cards']

class GOAEndTurnActionCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GOAEndTurnActionCommand
        fields = []
        
class GOAEndCongressActionCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GOAEndCongressActionCommand
        fields = []

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
        if action_command_type is GOAChooseRevealingBoardCardActionCommand:
            return GOAChooseRevealingBoardCardActionCommandSerializer(action.action_command).data
        if action_command_type is GOAChooseOpenBoardCardActionCommand:
            return GOAChooseOpenBoardCardActionCommandSerializer(action.action_command).data
        if action_command_type is GOAUseMaskActionCommand:
            return GOAUseMaskActionCommandSerializer(action.action_command).data
        if action_command_type is GOAUseReformActionCommand:
            return GOAUseReformActionCommandSerializer(action.action_command).data
        if action_command_type is GOAUseExpandActionCommand:
            return GOAUseExpandActionCommandSerializer(action.action_command).data
        if action_command_type is GOAReleaseCardsActionCommand:
            return GOAReleaseCardsActionCommandSerializer(action.action_command).data
        if action_command_type is GOAUseStrategyActionCommand:
            return GOAUseStrategyActionCommandSerializer(action.action_command).data
        if action_command_type is GOAEndTurnActionCommand:
            return GOAEndTurnActionCommandSerializer(action.action_command).data
        
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
    
class GOAGameBoardRevealingSerializer(serializers.ModelSerializer):
    board = GOABoardRevealingSerializer(read_only=True)
    players = serializers.SerializerMethodField(method_name='get_players')
    setting = GOASettingSerializer(read_only=True)
    
    class Meta:
        model = GOAGame
        fields = ['id', 'board', 'players', 'setting']

    def get_players(self, game: GOAGame):
        return GOAPlayerSerializer(game.player_set.players.all(), many = True).data