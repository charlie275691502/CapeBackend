import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async

from Common.GameModel import GameModel
from Common.DataLoader import DataLoader, Constant, GOACharacter
from .models import Message, Room
from TTTGame.models import TTTActionSet, TTTPlayerSet, TTTPlayer, TTTBoard, TTTGame, TTTRecord, TTTSetting
from GOAGame.models import GOAActionSet, GOAPlayerSet, GOAPlayer, GOABoard, GOAGame, GOARecord, GOASetting
from .serializers import MessageSerializer, RoomListSerializer
from TTTGame.serializers import TTTGameSerializer
from GOAGame.serializers import GOAGameSerializer
from core.management.commands.load_game_data import game_data


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

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name)

        data = await database_sync_to_async(self.leave_room)(
            room_id,
            player_id)
        
        if data != None :
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_data",
                    "command": "update_room",
                    "data": data
                })

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
            # data = await database_sync_to_async(self.create_ttt_game) (
            #     room_id)
            #
            # await self.channel_layer.group_send(
            #     self.room_group_name,
            #     {
            #         "type": "send_data",
            #         "command": "start_ttt_game",
            #         "data": data
            #     })
            # await self.send_command_success(command)
            
            data = await database_sync_to_async(self.create_goa_game) (
                room_id)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_data",
                    "command": "start_goa_game",
                    "data": data
                })
            await self.send_command_success(command)
            
        elif command == "join_room" :
            isSuccess, data, errorMessage = await database_sync_to_async(self.try_join_room)(
                room_id,
                player_id)

            if isSuccess == False :
                await self.send_command_fail(command, errorMessage)
            else :
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "send_data",
                        "command": "update_room",
                        "data": data
                    })
                await self.send_command_success(command)
    
    async def send_command_success(self, command):
        await self.send(text_data=json.dumps({"command": f"{command}_success", "data": ""}))

    async def send_command_fail(self, command, errorMessage):
        await self.send(text_data=json.dumps({"command": f"{command}_fail", "data": {"error": errorMessage}}))

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
        if room == None :
            return (False, None, "Room Not Exists")

        players = room.players.all()
        if len(players) >= room.game_setting.player_plot:
            return (False, None, "Room Full")

        player = room.players.filter(user_id=player_id).first()
        if player != None :
            return (False, None, "You are already in this room")
        
        room.players.add(player_id)
        room.save()

        serializer = RoomListSerializer(room)
        return (True, serializer.data, "")
    
    def leave_room(self, room_id, player_id):
        room = Room.objects.filter(id=room_id).first()
        if room == None :
            return None

        player = room.players.filter(pk=player_id).first()
        if player == None :
            return None
        
        players = room.players.all()
        if len(players) == 1 :
            room.delete()
            return None

        room.players.remove(player_id)
        room.save()
        
        serializer = RoomListSerializer(room)
        return serializer.data

    def create_ttt_game(self, room_id):
        board = TTTBoard.objects.create(positions=[0, 0, 0, 0, 0, 0, 0, 0, 0])
        init_board = TTTBoard.objects.create(positions=[0, 0, 0, 0, 0, 0, 0, 0, 0])
        action_set = TTTActionSet.objects.create()
        player_set = TTTPlayerSet.objects.create()
        setting = TTTSetting.objects.create(board_size=3)

        room = Room.objects.filter(id=room_id).first()
        players = room.players.all()
        team_index = 1
        for player in players :
            TTTPlayer.objects.create(team=team_index, player_id=player.user.id, player_set_id=player_set.id)
            team_index += 1

        game = TTTGame.objects.create(board_id=board.id, player_set_id=player_set.id, setting_id=setting.id)
        TTTRecord.objects.create(init_board_id=init_board.id, action_set_id=action_set.id, game_id=game.id)
        serializer = TTTGameSerializer(game)
        return serializer.data

    def create_goa_game(self, room_id):
        room = Room.objects.filter(id=room_id).first()
        players = room.players.all()
        
        game_model = GameModel.init(
            [player.user.id for player in players]
        )
        
        board = GOABoard.objects.create(
            draw_cards=game_model.draw_cards,
            grave_cards=game_model.grave_cards,
            board_cards=game_model.board_cards,
            strategy_cards=game_model.strategy_cards,
            open_board_card_positions=game_model.open_board_card_positions,
            revealing_player_id=game_model.revealing_player_id,
            revealing_board_card_positions=game_model.revealing_board_card_positions,
            turn=game_model.turn,
            player_ids=game_model.player_ids,
            taking_turn_player_id=game_model.taking_turn_player_id,
            chair_person_player_id=game_model.chair_person_player_id,
            phase=game_model.phase,
            is_last_turn=game_model.is_last_turn)
        
        init_board = GOABoard.objects.create(
            draw_cards=game_model.draw_cards,
            grave_cards=game_model.grave_cards,
            board_cards=game_model.board_cards,
            strategy_cards=game_model.strategy_cards,
            open_board_card_positions=game_model.open_board_card_positions,
            revealing_player_id=game_model.revealing_player_id,
            revealing_board_card_positions=game_model.revealing_board_card_positions,
            turn=game_model.turn,
            player_ids=game_model.player_ids,
            taking_turn_player_id=game_model.taking_turn_player_id,
            chair_person_player_id=game_model.chair_person_player_id,
            phase=game_model.phase,
            is_last_turn=game_model.is_last_turn)
        
        action_set = GOAActionSet.objects.create()
        player_set = GOAPlayerSet.objects.create()
        setting = GOASetting.objects.create()

        for player in players :
            GOAPlayer.objects.create(
                order=game_model.player_ids.index(player.user.id),
                is_bot=False,
                character_key=random.choice(game_data.characters.ids),
                public_cards=[],
                strategy_cards=[],
                power=0,
                power_limit=35,
                player_id=player.user.id,
                player_set_id=player_set.id)

        game = GOAGame.objects.create(board_id=board.id, player_set_id=player_set.id, setting_id=setting.id)
        GOARecord.objects.create(init_board_id=init_board.id, action_set_id=action_set.id, game_id=game.id)
        serializer = GOAGameSerializer(game)
        return serializer.data