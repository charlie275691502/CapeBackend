import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, Room
from .serializers import MessageSerializer, RoomPlayerSerializer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = "chat_%s" % room_id
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        room_id = self.scope["url_route"]["kwargs"]['room_id']
        player_id = self.scope["user"].id
        command = text_data_json["command"]

        if command == "send_message" :
            content = text_data_json["content"]
            data = await self.create_message(room_id, player_id, content)
        
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "send_message", "command": "send_message", "data": data}
            )
        elif command == "join_room" :
            data = await self.try_join_room(room_id, player_id)
        
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "update_room_players", "command": "update_room_players", "data": data}
            )

    async def send_message(self, event):
        data = event["data"]
        command = event["command"]
        await self.send(text_data=json.dumps({"command": command, "data": data}))

    async def update_room_players(self, event):
        data = event["data"]
        command = event["command"]
        await self.send(text_data=json.dumps({"command": command, "data": data}))

    @database_sync_to_async
    def create_message(self, room_id, player_id, content):
        message = Message.objects.create(room_id=room_id, player_id=player_id, content=content)
        serializer = MessageSerializer(message)
        return serializer.data
    
    @database_sync_to_async
    def try_join_room(self, room_id, player_id):
        room = Room.objects.filter(id=room_id).first()
        serializer = RoomPlayerSerializer(room)
        return serializer.data