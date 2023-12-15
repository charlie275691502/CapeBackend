import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from .models import Message, Room
from mainpage.models import Player
from .serializers import MessageSerializer, RoomListSerializer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = "chat_%s" % room_id
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        room_id = self.scope["url_route"]["kwargs"]["room_id"]
        player_id = self.scope["user"].id
        await database_sync_to_async(self.try_leave_room)(
            room_id,
            player_id)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        player_id = self.scope["user"].id
        command = text_data_json["command"]
        room_id = self.scope["url_route"]["kwargs"]['room_id']

        if command == "send_message" :
            content = text_data_json["content"]
            data = await database_sync_to_async(self.create_message) (
                room_id,
                player_id,
                content)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_data",
                    "command": "append_message",
                    "data": data
                })

        elif command == "start_game" :
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_data",
                    "command": "start_game",
                    "data": ""
                })
            
        elif command == "join_room" :
            isSuccess, data, errorMessage = await database_sync_to_async(self.try_join_room)(
                room_id,
                player_id)

            if isSuccess == False :
                await self.send(text_data=json.dumps({"command": "join_room_fail", "data": errorMessage}))
            else :
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "send_data",
                        "command": "update_room",
                        "data": data
                    })
                await self.send(text_data=json.dumps({"command": "join_room_success", "data": ""}))

        elif command == "leave_room" :
            isSuccess, data, errorMessage = await database_sync_to_async(self.try_leave_room)(
                room_id,
                player_id)
            
            if isSuccess == False :
                await self.send(text_data=json.dumps({"command": "leave_room_fail", "data": errorMessage}))
            else :
                if data != None :
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "send_data",
                            "command": "update_room",
                            "data": data
                        })
                await self.send(text_data=json.dumps({"command": "leave_room_success", "data": ""}))

    async def send_data(self, event):
        command = event["command"]
        data = event["data"]
        await self.send(text_data=json.dumps({"command": command, "data": data}))

    def create_message(self, room_id, player_id, content):
        message = Message.objects.create(room_id=room_id, player_id=player_id, content=content)
        serializer = MessageSerializer(message)
        return serializer.data
    
    def try_join_room(self, room_id, player_id):
        room = Room.objects.filter(id=room_id).first()
        players = room.players.all()
        player = players.filter(pk=player_id)
        if len(players) >= 4:
            return (False, None, "Room Full")
        elif player.exists() :
            return (False, None, "You are already in this room")
        else :
            room.players.add(player_id)
            room.save()

        serializer = RoomListSerializer(room)
        return (True, serializer.data, "")
    
    def try_leave_room(self, room_id, player_id):
        room = Room.objects.filter(id=room_id).first()
        players = room.players.all()
        player = players.filter(pk=player_id)
        if player.exists() :
            room.players.remove(player_id)
        else :
            return (False, None, "You are not in this room")
        
        if len(players) == 0 :
            room.delete()
            return (True, None, "")
        
        serializer = RoomListSerializer(room)
        return (True, serializer.data, "")