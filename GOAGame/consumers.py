import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from Common.DataLoader import CardType, GOACardTypePowerPair
from Common.GameModel import GameModel
from core.management.commands.load_game_data import game_data
from .models import GOAChooseOpenBoardCardActionCommand, GOAChooseRevealingBoardCardActionCommand, GOAEndCongressActionCommand, GOAEndTurnActionCommand, GOAGame, GOAAction, GOAPlayer, GOARecord, GOAReleaseCardsActionCommand, GOARevealBoardCardsActionCommand, GOASummary, GOAUseExpandActionCommand, GOAUseMaskActionCommand, GOAUseReformActionCommand, GOAUseStrategyActionCommand
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
            case "use_mask_action":
                await self.use_mask_action(text_data_json, player_id, command)
            case "use_reform_action":
                await self.use_reform_action(text_data_json, player_id, command)
            case "use_expand_action":
                await self.use_expand_action(text_data_json, player_id, command)
            case "release_cards_action":
                await self.release_cards_action(text_data_json, player_id, command)
            case "use_strategy_action":
                await self.use_strategy_action(text_data_json, player_id, command)
            case "end_turn_action":
                await self.end_turn_action(text_data_json, player_id, command)
            case "end_congress_action":
                await self.end_congress_action(text_data_json, player_id, command)
    
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
        def create_command(player_id, positions):
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
        
        await database_sync_to_async(create_command)(player_id, positions)
        await self.game_model.reveal_board_cards(self.game, player_id, positions)
        
        await self.update_game()
        await self.group_send()
        await self.send_command_success(command)
    
    async def choose_revealing_board_card_action(self, text_data_json, player_id, command):
        def create_command(player_id, position):
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
        
        await database_sync_to_async(create_command)(player_id, position)
        await self.game_model.choose_revealing_board_card(self.game, player_id, position)
        
        await self.update_game()
        await self.group_send()
        await self.send_command_success(command)
    
    async def choose_open_board_card_action(self, text_data_json, player_id, command):
        def create_command(player_id, position):
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
        
        await database_sync_to_async(create_command)(player_id, position)
        await self.game_model.choose_open_board_card(self.game, player_id, position)
        
        await self.update_game()
        await self.group_send()
        await self.send_command_success(command)
    
    async def use_mask_action(self, text_data_json, player_id, command):
        def create_command(player_id, card):
            action_command = GOAUseMaskActionCommand.objects.create(card=card)
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
            
        if self.game_model.is_player_mask_used[player_id] :
            await self.send_command_fail(command, "Mask has been used in this turn")
            return
        
        card = text_data_json["card"]
        goa_card = game_data.cards.get_row(str(card))
        
        if card not in self.game_model.player_public_cards[player_id]:
            await self.send_command_fail(command, f"card id {card} not found in your hand")
            return
            
        if goa_card.card_type != CardType.ActionMask:
            await self.send_command_fail(command, "Invalid mask card")
            return
        
        await database_sync_to_async(create_command)(player_id, card)
        await self.game_model.use_mask(self.game, player_id, card)
        
        await self.update_game()
        await self.group_send()
        await self.send_command_success(command)
    
    async def use_reform_action(self, text_data_json, player_id, command):
        def create_command(player_id, card, target_card):
            action_command = GOAUseReformActionCommand.objects.create(card=card, target_card=target_card)
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
            
        if self.game_model.is_player_reform_used[player_id] :
            await self.send_command_fail(command, "Reform has been used in this turn")
            return
        
        card = text_data_json["card"]
        goa_card = game_data.cards.get_row(str(card))
        target_card = text_data_json["target_card"]
        goa_target_card = game_data.cards.get_row(str(target_card))
        
        if card not in self.game_model.player_public_cards[player_id]:
            await self.send_command_fail(command, f"card id {card} not found in your hand")
            return
        
        if target_card not in self.game_model.player_public_cards[player_id]:
            await self.send_command_fail(command, f"target_card id {card} not found in your hand")
            return
            
        if goa_card.card_type != CardType.ActionReform:
            await self.send_command_fail(command, "Invalid reform card")
            return
            
        if goa_target_card.card_type != CardType.Power:
            await self.send_command_fail(command, "Cannot reform non-power cards")
            return
            
        if goa_card.power_type != goa_target_card.power_type:
            await self.send_command_fail(command, "Cannot reform card of different power types")
            return
        
        await database_sync_to_async(create_command)(player_id, card, target_card)
        await self.game_model.use_reform(self.game, player_id, card, target_card)
        
        await self.update_game()
        await self.group_send()
        await self.send_command_success(command)
    
    async def use_expand_action(self, text_data_json, player_id, command):
        def create_command(player_id, card, target_position):
            action_command = GOAUseExpandActionCommand.objects.create(card=card, target_position=target_position)
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
            
        if self.game_model.is_player_expand_used[player_id] :
            await self.send_command_fail(command, "Expand has been used in this turn")
            return
        
        card = text_data_json["card"]
        goa_card = game_data.cards.get_row(str(card))
        target_position = text_data_json["target_position"]
        
        if target_position not in self.game_model.open_board_card_positions or self.game_model.board_cards[target_position] == -1:
            await self.send_command_fail(command, "Must choose open card")
            return
        
        goa_target_card = game_data.cards.get_row(str(self.game_model.board_cards[target_position]))
        
        if card not in self.game_model.player_public_cards[player_id]:
            await self.send_command_fail(command, f"card id {card} not found in your hand")
            return
            
        if goa_card.card_type != CardType.ActionExpand:
            await self.send_command_fail(command, "Invalid expand card")
            return
            
        if goa_target_card.card_type != CardType.Power:
            await self.send_command_fail(command, "Cannot expand non-power cards")
            return
            
        if goa_card.power_type != goa_target_card.power_type:
            await self.send_command_fail(command, "Cannot expand card of different power types")
            return
        
        await database_sync_to_async(create_command)(player_id, card, target_position)
        await self.game_model.use_expand(self.game, player_id, card, target_position)
        
        await self.update_game()
        await self.group_send()
        await self.send_command_success(command)
        
    async def release_cards_action(self, text_data_json, player_id, command):
        def create_command(player_id, cards):
            action_command = GOAReleaseCardsActionCommand.objects.create(cards=cards)
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
        
        cards = text_data_json["cards"]
        goa_cards = [game_data.cards.get_row(str(card)) for card in cards]
        
        if len(cards) < 3:
            await self.send_command_fail(command, "Should select at least 3 cards")
            return
        
        if any([card for card in cards if card not in self.game_model.player_public_cards[player_id]]):
            await self.send_command_fail(command, "Cards not found in your hand")
            return
            
        if any([goa_card for goa_card in goa_cards if goa_card.card_type != CardType.Power]):
            await self.send_command_fail(command, "Can only use power cards")
            return
            
        if any([goa_card for goa_card in goa_cards if goa_card.power_type != goa_cards[0].power_type]):
            await self.send_command_fail(command, "Cards are not same power type")
            return
            
        sorted_goa_cards = sorted(goa_cards, key=lambda goa_card: goa_card.power)
        if any([x2.power - x1.power != 1 for x1, x2 in zip(sorted_goa_cards[:-1], sorted_goa_cards[1:])]) :
            await self.send_command_fail(command, "Cards are not continuous")
            return
        
        await database_sync_to_async(create_command)(player_id, cards)
        await self.game_model.release_cards(self.game, player_id, cards)
        
        await self.update_game()
        await self.group_send()
        await self.send_command_success(command)
        
    async def use_strategy_action(self, text_data_json, player_id, command):
        def create_command(player_id, card, requirement_cards):
            action_command = GOAUseStrategyActionCommand.objects.create(card=card, requirement_cards=requirement_cards)
            GOAAction.objects.create(
                action_set_id=self.record_action_set_id,
                player_id=player_id,
                action_command=action_command)
            
        if self.game_model.taking_turn_player_id != player_id:
            await self.send_command_fail(command, "Not your turn")
            return
            
        if self.game_model.phase != GameModel.ACTION_PHASE and self.game_model.phase != GameModel.CONGRESS_PHASE :
            await self.send_command_fail(command, "Not action and congress phase")
            return
            
        if self.game_model.is_player_strategy_used[player_id] :
            await self.send_command_fail(command, "Strategy card has been used in this turn")
            return
        
        card = text_data_json["card"]
        requirement_cards = text_data_json["requirement_cards"]
        goa_card = game_data.cards.get_row(str(card))
        goa_requirement_cards = [game_data.cards.get_row(str(requirement_card)) for requirement_card in requirement_cards]
        goa_requirement_card_pairs = [GOACardTypePowerPair(goa_requirement_card.power_type, goa_requirement_card.power) for goa_requirement_card in goa_requirement_cards]
        goa_requirement_card_pairs.sort(key=lambda pair: pair.get_order())
        
        if card not in self.game_model.player_strategy_cards[player_id]:
            await self.send_command_fail(command, f"Card id {card} not found in your hand")
            return
        
        if any([requirement_card for requirement_card in requirement_cards if requirement_card not in self.game_model.player_public_cards[player_id]]):
            await self.send_command_fail(command, "Cards not found in your hand")
            return
            
        if goa_card.card_type != CardType.Strategy:
            await self.send_command_fail(command, "Invalid strategy card")
            return
            
        if len(goa_card.requirements) != len(requirement_cards):
            await self.send_command_fail(command, "Requirements count not match")
            return
            
        if any([a.power_type != b.power_type or a.power > b.power for (a, b) in zip(goa_card.requirements, goa_requirement_card_pairs)]):
            await self.send_command_fail(command, "Requirements not match")
            return
        
        await database_sync_to_async(create_command)(player_id, card, requirement_cards)
        await self.game_model.use_strategy(self.game, player_id, card, requirement_cards)
        
        await self.update_game()
        await self.group_send()
        await self.send_command_success(command)
        
    async def end_turn_action(self, text_data_json, player_id, command):
        def create_command(player_id):
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
        
        await database_sync_to_async(create_command)(player_id)
        await self.game_model.end_turn(self.game, player_id)
        
        await self.update_game()
        await self.group_send()
        await self.send_command_success(command)
        
    async def end_congress_action(self, text_data_json, player_id, command):
        def create_command(player_id):
            action_command = GOAEndCongressActionCommand.objects.create()
            GOAAction.objects.create(
                action_set_id=self.record_action_set_id,
                player_id=player_id,
                action_command=action_command)
            
        if self.game_model.is_player_end_congress[player_id] == True:
            await self.send_command_fail(command, "Already end congress")
            return
            
        if self.game_model.phase != GameModel.CONGRESS_PHASE:
            await self.send_command_fail(command, "Not congress phase")
            return
        
        await database_sync_to_async(create_command)(player_id)
        await self.game_model.end_congress(self.game, player_id)
        
        await self.update_game()
        await self.group_send()
        await self.send_command_success(command)