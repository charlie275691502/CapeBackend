import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from Common.DataLoader import DataLoader, GOACard
from Common.GameModel import GameModel
from .models import GOAGame, GOAAction, GOARecord, GOASummary
from .serializers import GOAActionSerializer, GOAGameSerializer, GOASummarySerializer
import gspread
from google.oauth2.service_account import Credentials

class GOAGameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        game_id = self.scope["url_route"]["kwargs"]["game_id"]
        
        record = await database_sync_to_async(self.get_record)(game_id)
        self.record_action_set_id = record.action_set.id
        self.game_id = game_id
        self.game_group_name = "game_%s" % game_id
        self.game_model = await database_sync_to_async(self.get_game_model)(game_id)
        
        (card_datas) = await self.load_datas()
        
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
        
        match command:
            case "choose_position_action":
                await database_sync_to_async(self.reveal_board_cards)()
            case "choose_position_action":
                await database_sync_to_async(self.choose_board_card)()
                

    
    async def send_command_success(self, command):
        await self.send(text_data=json.dumps({"command": f"{command}_success", "data": ""}))

    async def send_command_fail(self, command, errorMessage):
        await self.send(text_data=json.dumps({"command": f"{command}_fail", "data": errorMessage}))

    async def send_data(self, event):
        command = event["command"]
        data = event["data"]
        await self.send(text_data=json.dumps({"command": command, "data": data}))
        
    async def load_datas(self):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file('goawebsocket-2c1d9a4aecc4.json', scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open('GOA Websocket Datasheet')

        card_datas = DataLoader(sheet, "GOACards", GOACard)
        return card_datas
    
    def get_record(self, game_id: int):
        return GOARecord.objects.prefetch_related("action_set").filter(game_id=game_id).first()
    
    def get_player(self, game: GOAGame, player_id: int):
        return game.player_set.players.filter(player_id=player_id).first()
    
    def get_game_model(self, game_id: int):
        game = GOAGame.objects.filter(id=game_id).first()
        return GameModel.from_model(game)

    # def is_player_turn(self, game, player_id):
    #     return game.board.taking_turn_player_id == player_id

    def get_game_serializer(self, game):
        serializer = GOAGameSerializer(game)
        return serializer.data
    
    async def reveal_board_cards():
        pass
    
    async def choose_board_card():
        pass
    