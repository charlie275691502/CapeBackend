import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from Common.GameModel import GameModel
from .models import GOAChooseOpenBoardCardActionCommand, GOAChooseRevealingBoardCardActionCommand, GOAEndTurnActionCommand, GOAGame, GOAAction, GOAPlayer, GOARecord, GOARevealBoardCardsActionCommand, GOASummary
from .serializers import GOAActionSerializer, GOAGameBoardRevealingSerializer, GOAGameSerializer, GOASummarySerializer

class GOAGameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        game_id = self.scope["url_route"]["kwargs"]["game_id"]
        player_id = self.scope["user"].id
        
        record = await self.get_record(game_id)
        self.record_action_set_id = record.action_set.id
        self.game_id = game_id
        self.game_group_name = "game_%s" % game_id
        
        self.game = await self.get_game(game_id)
        self.game_model = await self.get_game_model(self.game)
        
        await self.channel_layer.group_add(
            self.game_group_name,
            self.channel_name)
        
        await self.channel_layer.group_add(
            self.get_player_group(player_id),
            self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        player_id = self.scope["user"].id
        
        await self.channel_layer.group_discard(
            self.game_group_name,
            self.channel_name)
        
        await self.channel_layer.group_discard(
            self.get_player_group(player_id),
            self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        player_id = self.scope["user"].id
        command = text_data_json["command"]
        
        match command:
            case "reveal_board_cards_action":
                await self.reveal_board_cards(text_data_json, player_id, command)
            case "choose_revealing_board_card_action":
                await self.choose_revealing_board_card_action(text_data_json, player_id, command)
            case "choose_open_board_card_action":
                await self.choose_open_board_card_action(text_data_json, player_id, command)
            case "end_turn_action":
                await self.end_turn_action(text_data_json, player_id, command)
    
    async def send_command_success(self, command):
        await self.send(text_data=json.dumps({"command": f"{command}_success", "data": ""}))

    async def send_command_fail(self, command, errorMessage):
        await self.send(text_data=json.dumps({"command": f"{command}_fail", "data": {"error": errorMessage}}))

    async def send_data(self, event):
        command = event["command"]
        data = event["data"]
        await self.send(text_data=json.dumps({"command": command, "data": data}))
        
    def get_player_group(self, player_id: int) -> str:
        return f"{self.game_group_name}_{player_id}"
    
    async def get_record(self, game_id: int) -> GOARecord:
        return await database_sync_to_async(
            lambda: GOARecord.objects.prefetch_related("action_set").filter(game_id=game_id).first()
        )()
    
    async def get_game(self, game_id: int) -> GOAGame:
        return await database_sync_to_async(
            lambda: GOAGame.objects.filter(id=game_id).first()
        )()
    
    async def get_players(self) -> list[GOAPlayer]:
        return await database_sync_to_async(
            lambda: list(self.game.player_set.players.select_related("player__user").all())
        )()
    
    async def get_player(self, player_id: int) -> GOAPlayer:
        return await database_sync_to_async(
            lambda: self.game.player_set.players.filter(player_id=player_id).first()
        )()
    
    async def get_game_serializer(self) -> GOAGameSerializer:
        return await database_sync_to_async(
            lambda: GOAGameSerializer(self.game).data
        )()
    
    async def get_game_board_revealing_serializer(self) -> GOAGameBoardRevealingSerializer:
        return await database_sync_to_async(
            lambda: GOAGameBoardRevealingSerializer(self.game).data
        )()
    
    async def get_game_model(self, game) -> GameModel:
        return await database_sync_to_async(
            lambda: GameModel.from_model(game)
        )()
    
    async def update_game(self):
        self.game = await self.get_game(self.game_id)
    
    async def group_send(self):
        gameBoardRevealingSerializer = await self.get_game_board_revealing_serializer()
        gameSerializer = await self.get_game_serializer()
        
        players = await self.get_players()
        for player in players:
            if player.player.user.id == self.game_model.taking_turn_player_id :
                await self.channel_layer.group_send(
                    self.get_player_group(player.player.user.id),
                    {
                        "type": "send_data",
                        "command": "update_game",
                        "data": gameBoardRevealingSerializer
                    })
            else :
                await self.channel_layer.group_send(
                    self.get_player_group(player.player.user.id),
                    {
                        "type": "send_data",
                        "command": "update_game",
                        "data": gameSerializer
                    })
    
    async def reveal_board_cards(self, text_data_json, player_id, command):
        def create_reveal_board_cards_action_command(player_id, positions):
            action_command = GOARevealBoardCardsActionCommand.objects.create(positions=positions)
            GOAAction.objects.create(
                action_set_id=self.record_action_set_id,
                player_id=player_id,
                action_command=action_command)
            
        if self.game_model.taking_turn_player_id != player_id:
            await self.send_command_fail(command, "Not your turn")
            return
            
        if self.game_model.phase != GameModel.CHOOSE_BOARD_CARD_PHASE:
            await self.send_command_fail(command, "Not choose board card phase")
            return
            
        if len(self.game_model.revealing_board_card_positions) > 0 :
            await self.send_command_fail(command, "Already chose revealed card")
            return
            
        positions = text_data_json["positions"]
        
        if any(position for position in positions if position in self.game_model.open_board_card_positions or self.game_model.board_cards[position] == -1) :
            await self.send_command_fail(command, "Must choose covered card")
            return
        
        await database_sync_to_async(create_reveal_board_cards_action_command)(player_id, positions)
        
        self.game_model.revealing_board_card_positions = positions
        self.game_model.revealing_player_id = player_id
        
        players = await self.get_players()
        await self.game_model.save_to_model(self.game, players)
        await self.update_game()
        await self.group_send()
        await self.send_command_success(command)
    
    async def choose_revealing_board_card_action(self, text_data_json, player_id, command):
        def create_choose_revealing_board_card_action_command(player_id, position):
            action_command = GOAChooseRevealingBoardCardActionCommand.objects.create(position=position)
            GOAAction.objects.create(
                action_set_id=self.record_action_set_id,
                player_id=player_id,
                action_command=action_command)
            
        if self.game_model.taking_turn_player_id != player_id:
            await self.send_command_fail(command, "Not your turn")
            return
            
        if self.game_model.phase != GameModel.CHOOSE_BOARD_CARD_PHASE:
            await self.send_command_fail(command, "Not choose board card phase")
            return
            
        if len(self.game_model.revealing_board_card_positions) == 0 :
            await self.send_command_fail(command, "haven't chosen revealed card")
            return
        
        position = text_data_json["position"]
        
        if position not in self.game_model.revealing_board_card_positions or self.game_model.board_cards[position] == -1:
            await self.send_command_fail(command, "Must choose revealed card")
            return
        
        await database_sync_to_async(create_choose_revealing_board_card_action_command)(player_id, position)
        
        self.game_model.player_cards[player_id].append(self.game_model.board_cards[position])
        self.game_model.board_cards[position] = -1
        self.game_model.open_board_card_positions.extend([revaling_board_card_position for revaling_board_card_position in self.game_model.revealing_board_card_positions if revaling_board_card_position != position]) 
        self.game_model.revealing_board_card_positions = []
        self.game_model.revealing_player_id = -1
        self.game_model.phase = GameModel.ACTION_PHASE

        players = await self.get_players()
        await self.game_model.save_to_model(self.game, players)
        await self.update_game()
        await self.group_send()
        await self.send_command_success(command)
    
    async def choose_open_board_card_action(self, text_data_json, player_id, command):
        def create_choose_open_board_card_action_command(player_id, position):
            action_command = GOAChooseOpenBoardCardActionCommand.objects.create(position=position)
            GOAAction.objects.create(
                action_set_id=self.record_action_set_id,
                player_id=player_id,
                action_command=action_command)
            
        if self.game_model.taking_turn_player_id != player_id:
            await self.send_command_fail(command, "Not your turn")
            return
            
        if self.game_model.phase != GameModel.CHOOSE_BOARD_CARD_PHASE:
            await self.send_command_fail(command, "Not choose board card phase")
            return
            
        if len(self.game_model.revealing_board_card_positions) > 0 :
            await self.send_command_fail(command, "Must Choose Revealed cards")
            return
        
        position = text_data_json["position"]
        
        if position not in self.game_model.open_board_card_positions or self.game_model.board_cards[position] == -1:
            await self.send_command_fail(command, "Must choose open card")
            return
        
        await database_sync_to_async(create_choose_open_board_card_action_command)(player_id, position)
        
        self.game_model.player_cards[player_id].append(self.game_model.board_cards[position])
        self.game_model.board_cards[position] = -1
        self.game_model.open_board_card_positions.remove(position) 
        self.game_model.phase = GameModel.ACTION_PHASE
        
        players = await self.get_players()
        await self.game_model.save_to_model(self.game, players)
        await self.update_game()
        await self.group_send()
        await self.send_command_success(command)
        
    async def end_turn_action(self, text_data_json, player_id, command):
        def create_end_turn_action_command(player_id):
            action_command = GOAEndTurnActionCommand.objects.create()
            GOAAction.objects.create(
                action_set_id=self.record_action_set_id,
                player_id=player_id,
                action_command=action_command)
            
        if self.game_model.taking_turn_player_id != player_id:
            await self.send_command_fail(command, "Not your turn")
            return
            
        if self.game_model.phase != GameModel.ACTION_PHASE:
            await self.send_command_fail(command, "Not action phase")
            return
        
        await database_sync_to_async(create_end_turn_action_command)(player_id)
        
        self.game_model.next_turn()
        # check game end
        
        players = await self.get_players()
        await self.game_model.save_to_model(self.game, players)
        await self.update_game()
        await self.group_send()
        await self.send_command_success(command)
        
    