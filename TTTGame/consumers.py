import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from .models import TTTGame, TTTAction, TTTChoosePositionActionCommand, TTTRecord, TTTSummary
from .serializers import TTTActionSerializer, TTTGameSerializer, TTTSummarySerializer

class TTTGameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        game_id = self.scope["url_route"]["kwargs"]["game_id"]
        
        record = await database_sync_to_async(self.get_record)(game_id)
        self.record_action_set_id = record.action_set.id
        self.game_id = game_id
        self.game_group_name = "game_%s" % game_id
        
        await self.channel_layer.group_add(
            self.game_group_name,
            self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.game_group_name,
            self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        player_id = self.scope["user"].id
        command = text_data_json["command"]


        if command == "choose_position_action" :
            game = await database_sync_to_async(self.get_game)(self.game_id)
            if await database_sync_to_async(self.is_player_turn)(game, player_id) == False:
                await self.send_command_fail(command, "Not your turn yet.")
                return
        
            position = text_data_json["position"]

            if await database_sync_to_async(self.is_position_valid)(game, position) == False:
                await self.send_command_fail(command, "Position invalid")
                return

            await database_sync_to_async(self.execute_choose_position_action) (
                game,
                player_id,
                position)

            data = await database_sync_to_async(self.get_game_serializer)(game)
            await self.channel_layer.group_send(
                self.game_group_name,
                {
                    "type": "send_data",
                    "command": "update_game",
                    "data": data
                })
            await self.send_command_success(command)

            is_game_over, is_team_1_win = self.is_game_over(game)
            if is_game_over :
                data = await database_sync_to_async(self.execute_game_over)(game, is_team_1_win)
                await self.channel_layer.group_send(
                    self.game_group_name,
                    {
                        "type": "send_data",
                        "command": "summary",
                        "data": data
                    })

    
    async def send_command_success(self, command):
        await self.send(text_data=json.dumps({"command": f"{command}_success", "data": ""}))

    async def send_command_fail(self, command, errorMessage):
        await self.send(text_data=json.dumps({"command": f"{command}_fail", "data": {"error": errorMessage}}))

    async def send_data(self, event):
        command = event["command"]
        data = event["data"]
        await self.send(text_data=json.dumps({"command": command, "data": data}))

    def get_game(self, game_id):
        return TTTGame.objects.filter(id=game_id).first()
    
    def get_record(self, game_id):
        return TTTRecord.objects.prefetch_related("action_set").filter(game_id=game_id).first()
    
    def get_player(self, game, player_id):
        return game.player_set.players.filter(player_id=player_id).first()

    def is_player_turn(self, game, player_id):
        player = game.player_set.players.filter(player_id=player_id).first()
        return game.board.turn_of_team == player.team

    def is_position_valid(self, game, position):
        positions = game.board.positions
        return 0 <= position and position < game.setting.board_size ** 2 and positions[position] == 0

    def is_game_over(self, game):
        board_size = game.setting.board_size
        column_team_count = [[0 for index in range(board_size)] for team in range(2)]
        row_team_count = [[0 for index in range(board_size)] for team in range(2)]
        diagonal_team_count = [[0, 0] for team in range(2)]
        positions = game.board.positions
        for index, position in enumerate(positions) :
            column_index = index % board_size
            row_index = index // board_size
            if position == 0 :
                continue
            team_index = position - 1
            column_team_count[team_index][column_index] += 1
            row_team_count[team_index][row_index] += 1
            diagonal_team_count[team_index][0] += 1 if row_index == column_index else 0
            diagonal_team_count[team_index][1] += 1 if row_index + column_index + 1 == board_size else 0
        
        is_team_1_win = \
            any([count == board_size for count in column_team_count[0]]) or\
            any([count == board_size for count in row_team_count[0]]) or\
            any([count == board_size for count in diagonal_team_count[0]])
            
        is_team_2_win = \
            any([count == board_size for count in column_team_count[1]]) or\
            any([count == board_size for count in row_team_count[1]]) or\
            any([count == board_size for count in diagonal_team_count[1]])
            
        return (is_team_1_win or is_team_2_win, is_team_1_win)

    def execute_choose_position_action(self, game, player_id, position):
        player = self.get_player(game, player_id)
        action_command = TTTChoosePositionActionCommand.objects.create(position=position)
        TTTAction.objects.create(
            action_set_id=self.record_action_set_id,
            player_id=player.player.user.id,
            action_command=action_command)
        
        team = player.team
        game.board.positions[position] = team
        game.board.turn += 1 
        game.board.turn_of_team = 3 - team
        game.board.save()
        
    def execute_game_over(self, game, is_team_1_win):
        record = self.get_record(self.game_id)
        summary = TTTSummary.objects.create(winner= \
                                                    game.player_set.players.filter(team=1).first() \
                                                if is_team_1_win else \
                                                    game.player_set.players.filter(team=1).first() \
                                                , turns=game.board.turn)
        record.summary = summary
        record.save()
        
        serializer = TTTSummarySerializer(summary)
        return serializer.data

    def get_game_serializer(self, game):
        serializer = TTTGameSerializer(game)
        return serializer.data
