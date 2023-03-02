import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message
from .serializers import MessageSerializer


class ChatConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def create_message(self, room_id, player_id, content):
        message = Message.objects.create(room_id=room_id, player_id=player_id, content=content)
        serializer = MessageSerializer(message)
        return serializer.data

    async def connect(self):
        room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = "chat_%s" % room_id

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        room_id = self.scope["url_route"]["kwargs"]['room_id']
        player_id = self.scope["user"].id
        command = text_data_json["command"]

        if command == "send_message" :
            content = text_data_json["content"]
            data = await self.create_message(room_id, player_id, content)
        
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat_message", "command": "send_message", "data": data}
            )

    # Receive message from room group
    async def chat_message(self, event):
        data = event["data"]
        command = event["command"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"command": command, "data": data}))