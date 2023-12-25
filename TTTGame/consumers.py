import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from .models import TTTGame, TTTAction, TTTChoosePositionActionCommand
from .serializers import TTTActionSerializer, TTTGameSerializer

class TTTGameConsumer(AsyncWebsocketConsumer):
    def __init__(self):
        game_id = self.scope["url_route"]["kwargs"]["game_id"]
        self.game = self.get_board(game_id)

    async def connect(self):
        game_id = self.scope["url_route"]["kwargs"]["game_id"]
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

        if self.is_player_turn(player_id) == False:
            await self.send_command_fail(command, "Not your turn yet.")
            return

        if command == "choose_position_action" :
            position = text_data_json["position"]

            if self.is_position_valid(position) == False:
                await self.send_command_fail(command, "Position invalid")
                return

            data = await database_sync_to_async(self.create_choose_position_action) (
                player_id,
                position)

            await database_sync_to_async(self.execute_choose_position_action) (
                player_id,
                position)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_data",
                    "command": "choose_position_action",
                    "data": data
                })
            await self.send_command_success(command)

            if self.is_game_over() :
                data = self.get_game_serializer()
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "send_data",
                        "command": "game_over",
                        "data": data
                    })

    
    async def send_command_success(self, command):
        await self.send(text_data=json.dumps({"command": f"{command}_success", "data": ""}))

    async def send_command_fail(self, command, errorMessage):
        await self.send(text_data=json.dumps({"command": f"{command}_fail", "data": errorMessage}))

    async def send_data(self, event):
        command = event["command"]
        data = event["data"]
        await self.send(text_data=json.dumps({"command": command, "data": data}))

    def get_board(self, game_id):
        return TTTGame.objects.filter(id=game_id).first()

    def is_player_turn(self, player_id):
        player = self.game.player_set.players.filter(id=player_id).first()
        return self.game.board.turn_of_team == player.team

    def is_position_valid(self, position):
        positions = self.game.board.positions
        return 0 <= position and position < self.game.setting.board_size ** 2 and positions[position] == 0

    def is_game_over(self):
        board_size = self.game.setting.board_size
        column_team_count = [[0 for index in board_size] for team in range(2)]
        row_team_count = [[0 for index in board_size] for team in range(2)]
        diagonal_team_count = [[0, 0] for team in range(2)]
        row_count = []
        positions = self.game.board.positions
        for index, position in enumerate(positions)
            column_index = index % board_size
            row_index = index / board_size
            if position == 0 :
                continue
            team_index = position - 1
            column_team_count[team_index][column_index] += 1
            row_team_count[team_index][row_index] += 1
            diagonal_team_count[team_index][0] += 1 if row_index == column_index else 0
            diagonal_team_count[team_index][1] += 1 if row_index + column_index + 1 == board_size else 0
        
        return any([any([count == board_size for count in column_count]) for column_count in column_team_count]) or\
               any([any([count == board_size for count in row_count]) for row_count in row_team_count]) or\
               any([any([count == board_size for count in diagonal_count]) for diagonal_count in diagonal_team_count])

    def create_choose_position_action(self, player_id, position):
        player = self.game.player_set.players.filter(id=player_id).first()

        action_command = TTTChoosePositionActionCommand.objects.create(position=position)
        action = TTTAction.objects.create(
            action_set_id=self.game.player_set.action_set.id,
            player_id=player.player.user.id,
            action_command=action_command)

        serializer = TTTActionSerializer(action)
        return serializer.data

    def execute_choose_position_action(self, player_id, position):
        player = self.game.player_set.players.filter(id=player_id).first()
        team = player.team
        self.game.board.positions[position] = team
        self.game.board.turn += 1 
        self.game.board.turn_of_team = 3 - team
        self.game.board.save()

    def get_game_serializer(self):
        serializer = TTTGameSerializer(self.game)
        return serializer.data
