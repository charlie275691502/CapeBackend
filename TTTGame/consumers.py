import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from .models import TTTGame, TTTAction, TTTChoosePositionActionCommand
from .serializers import TTTActionSerializer

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
        return 0 <= position and position < self.game.setting.board_size ** 2 and self.game.board.positions[position] == 0

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
        self.game.board.position[position] = team
        self.game.board.save()
