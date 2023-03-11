import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Message, Room
from mainpage.models import Player
from .serializers import MessageSerializer, RoomListSerializer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = "chat_%s" % room_id

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        player_id = self.scope["user"].id
        rooms = Player.objects.filter(user_id=player_id).first().rooms.all()
        for room in rooms :
            self.try_leave_room(room.id, player_id)

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        player_id = self.scope["user"].id
        command = text_data_json["command"]

        if command == "send_message" :
            room_id = self.scope["url_route"]["kwargs"]['room_id']
            content = text_data_json["content"]
            data = self.create_message(room_id, player_id, content)
            
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, {
                    "type": "send_data",
                    "command": "append_message",
                    "data": data
                }
            )
        elif command == "join_room" :
            room_id = text_data_json['room_id']
            isSuccess, data, errorMessage = self.try_join_room(room_id, player_id)

            if isSuccess == False :
                self.send(text_data=json.dumps({"command": "join_room_fail", "data": errorMessage}))
            else :
                self.send(text_data=json.dumps({"command": "join_room_success", "data": None}))
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name, {
                        "type": "send_data",
                        "command": "update_room",
                        "data": data
                    }
                )
        elif command == "leave_room" :
            room_id = text_data_json['room_id']
            isSuccess, data, errorMessage = self.try_leave_room(room_id, player_id)
            
            if isSuccess == False :
                self.send(text_data=json.dumps({"command": "leave_room_fail", "data": errorMessage}))
            else :
                self.send(text_data=json.dumps({"command": "leave_room_success", "data": None}))
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name, {
                        "type": "send_data",
                        "command": "update_room",
                        "data": data
                    }
                )

    def send_data(self, event):
        data = event["data"]
        command = event["command"]
        self.send(text_data=json.dumps({"command": command, "data": data}))

    def create_message(self, room_id, player_id, content):
        message = Message.objects.create(room_id=room_id, player_id=player_id, content=content)
        serializer = MessageSerializer(message)
        return serializer.data
    
    def try_join_room(self, room_id, player_id):
        room = Room.objects.filter(id=room_id).first()
        players = room.players.all()
        player = players.filter(pk=player_id)
        if len(players) >= 4:
            # send error message to the player
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
            # send error message to the player
            return (False, None, "You are not in this room")
        serializer = RoomListSerializer(room)
        return (True, serializer.data, "")