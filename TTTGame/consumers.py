import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async

class TTTGameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        game_id = self.scope["url_route"]["kwargs"]["game_id"]
        self.game_group_name = "game_%s" % game_id
        
        await self.channel_layer.group_add(
            self.game_group_name,
            self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        game_id = self.scope["url_route"]["kwargs"]["game_id"]
        player_id = self.scope["user"].id
        await database_sync_to_async(self.try_leave_room)(
            game_id,
            player_id)

        await self.channel_layer.group_discard(
            self.game_group_name,
            self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        player_id = self.scope["user"].id
        game_id = self.scope["url_route"]["kwargs"]['game_id']
        command = text_data_json["command"]

    async def send_data(self, event):
        command = event["command"]
        data = event["data"]
        await self.send(text_data=json.dumps({"command": command, "data": data}))