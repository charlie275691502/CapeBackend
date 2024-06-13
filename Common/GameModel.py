import random

from Common.DataLoader import CardType, PowerType
from GOAGame.models import GOABoard, GOAGame, GOAPlayer
from channels.db import database_sync_to_async
from core.management.commands.load_game_data import game_data

class GameModel:
    def __init__(self,
                 draw_cards,
                 grave_cards,
                 board_cards_slot,
                 board_cards,
                 open_board_card_positions,
                 revealing_player_id,
                 revealing_board_card_positions,
                 player_public_cards,
                 player_strategy_cards,
                 player_powers,
                 player_power_limits,
                 player_ids,
                 taking_turn_player_id,
                 turn,
                 phase,
                 is_mask_used,
                 is_reform_used,
                 is_expand_used):
        
        self.draw_cards = draw_cards
        self.grave_cards = grave_cards
        self.board_cards_slot = board_cards_slot
        self.board_cards = board_cards
        self.open_board_card_positions = open_board_card_positions
        self.revealing_player_id = revealing_player_id
        self.revealing_board_card_positions = revealing_board_card_positions
        self.player_public_cards = player_public_cards
        self.player_strategy_cards = player_strategy_cards
        self.player_powers = player_powers
        self.player_power_limits = player_power_limits
        self.player_ids = player_ids
        self.taking_turn_player_id = taking_turn_player_id
        self.turn = turn
        self.phase = phase
        self.is_mask_used = is_mask_used
        self.is_reform_used = is_reform_used
        self.is_expand_used = is_expand_used
        pass

    @classmethod
    def init(cls, public_card_count: int, player_ids: list[int]):
        random.shuffle(player_ids)
        model = cls([card for card in range(1, public_card_count + 1)],
                    [],
                    len(player_ids) * 3,
                    [-1 for i in range(len(player_ids) * 3)],
                    [],
                    -1,
                    [],
                    {player_id: [] for player_id in player_ids},
                    {player_id: [] for player_id in player_ids},
                    {player_id: 0 for player_id in player_ids},
                    {player_id: 35 for player_id in player_ids},
                    player_ids,
                    player_ids[0],
                    1,
                    1,
                    False,
                    False,
                    False)
        model.refill_board_cards()
        return model
        
    
    @classmethod
    def from_model(cls, game: GOAGame):
        return cls(game.board.draw_cards,
                   game.board.grave_cards,
                   len(game.board.player_ids),
                   game.board.board_cards,
                   game.board.open_board_card_positions,
                   game.board.revealing_player_id,
                   game.board.revealing_board_card_positions,
                   {player.player.user.id: player.public_cards for player in game.player_set.players.all()},
                   {player.player.user.id: player.strategy_cards for player in game.player_set.players.all()},
                   {player.player.user.id: player.power for player in game.player_set.players.all()},
                   {player.player.user.id: player.power_limit for player in game.player_set.players.all()},
                   game.board.player_ids,
                   game.board.taking_turn_player_id,
                   game.board.turn,
                   game.board.phase,
                   game.board.is_mask_used,
                   game.board.is_reform_used,
                   game.board.is_expand_used)
        
    async def save_to_model(self, game: GOAGame):
        game.board.draw_cards = self.draw_cards
        game.board.grave_cards =  self.grave_cards
        game.board.board_cards = self.board_cards
        game.board.open_board_card_positions = self.open_board_card_positions
        game.board.revealing_player_id = self.revealing_player_id
        game.board.revealing_board_card_positions = self.revealing_board_card_positions
        game.board.taking_turn_player_id = self.taking_turn_player_id
        game.board.turn = self.turn
        game.board.phase = self.phase
        game.board.is_mask_used = self.is_mask_used
        game.board.is_reform_used = self.is_reform_used
        game.board.is_expand_used = self.is_expand_used
        await self.save_board(game.board)
        
        players = await self.get_players(game)
        for player_id in self.player_public_cards.keys() :
            player = next(player for player in players if player.player.user.id == player_id)
            player.public_cards = self.player_public_cards[player_id]
            player.strategy_cards = self.player_strategy_cards[player_id]
            player.power = self.player_powers[player_id]
            player.power_limit = self.player_power_limits[player_id]
            await self.save_player(player)
        
    async def save_board(self, board: GOABoard):
        return await database_sync_to_async(
            lambda: board.save()
        )()
        
    async def save_player(self, player: GOAPlayer):
        return await database_sync_to_async(
            lambda: player.save()
        )()
    
    async def get_players(self, game: GOAGame) -> list[GOAPlayer]:
        return await database_sync_to_async(
            lambda: list(game.player_set.players.select_related("player__user").all())
        )()
        
    CHOOSE_BOARD_CARD_PHASE = 1
    ACTION_PHASE = 2
        
    def refill_board_cards(self):
        for i in range(len(self.board_cards)) :
            if self.board_cards[i] == -1 :
                card = self.draw_one_public_card()
                self.board_cards[i] = card
                
    def refill_draw_cards(self):
        self.draw_cards.extend(self.grave_cards)
        self.grave_cards = []
    
    def draw_one_public_card(self) -> int:
        if (len(self.draw_cards) == 0) :
            self.refill_draw_cards()
        card = random.choice(self.draw_cards)
        self.draw_cards.remove(card)
        return card
    
    def draw_card_to_hand(self, player_id: int):
        self.player_public_cards[player_id].append(self.draw_one_public_card())
    
    def take_open_card_to_hand(self, player_id: int, position):
        self.player_public_cards[player_id].append(self.board_cards[position])
        self.board_cards[position] = -1
        self.open_board_card_positions.remove(position)
    
    def remove_card(self, player_id: int, card: int) -> int:
        self.player_public_cards[player_id].remove(card)
        self.grave_cards.append(card)
    
    def remove_cards(self, player_id: int, cards: list[int]) -> int:
        for card in cards:
            self.remove_cards(player_id, card)
        
    def update_power(self, player_id: int):
        goa_cards = [game_data.cards.get_row(str(card)) for card in self.player_public_cards[player_id]]
        power = 0
        for power_type in PowerType:
            power_cards = [goa_card for goa_card in goa_cards if goa_card.card_type == CardType.Power and goa_card.power_type == power_type]
            action_cards = [goa_card for goa_card in goa_cards if goa_card.is_action_card() and goa_card.power_type == power_type]
            mask_count = len([goa_card for goa_card in goa_cards if goa_card.card_type == CardType.ActionMask and goa_card.power_type == power_type])
            power += sum([goa_card.power for goa_card in power_cards[mask_count:] + action_cards])
        self.player_powers[player_id] = power
    
# action from consumer
    async def reveal_board_cards(self, game: GOAGame, player_id: int, positions: list[int]):
        self.revealing_board_card_positions = positions
        self.revealing_player_id = player_id
        await self.save_to_model(game)
    
    async def choose_revealing_board_card(self, game: GOAGame, player_id: int, position: int):
        self.player_public_cards[player_id].append(self.board_cards[position])
        self.update_power(player_id)
        self.board_cards[position] = -1
        self.open_board_card_positions.extend([revaling_board_card_position for revaling_board_card_position in self.revealing_board_card_positions if revaling_board_card_position != position]) 
        self.revealing_board_card_positions = []
        self.revealing_player_id = -1
        self.phase = GameModel.ACTION_PHASE
        await self.save_to_model(game)
        
    async def choose_open_board_card(self, game: GOAGame, player_id: int, position: int):
        self.take_open_card_to_hand(player_id, position)
        self.update_power(player_id)
        self.phase = GameModel.ACTION_PHASE
        await self.save_to_model(game)
        
    async def use_mask(self, game: GOAGame, player_id: int, card: int):
        self.remove_card(player_id, card)
        self.draw_card_to_hand(player_id)
        self.update_power(player_id)
        self.is_mask_used = True
        await self.save_to_model(game)
        
    async def use_reform(self, game: GOAGame, player_id: int, card: int, target_card: int):
        self.remove_card(player_id, card)
        self.remove_card(player_id, target_card)
        self.update_power(player_id)
        self.is_reform_used = True
        await self.save_to_model(game)
        
    async def use_expand(self, game: GOAGame, player_id: int, card: int, target_position: int):
        self.remove_card(player_id, card)
        self.take_open_card_to_hand(player_id, target_position)
        self.update_power(player_id)
        self.is_expand_used = True
        await self.save_to_model(game)
        
    async def end_turn(self, game: GOAGame):
        # check game end
        
        # check if refill cards
        
        index = self.player_ids.index(self.taking_turn_player_id)
        self.taking_turn_player_id = self.player_ids[(index + 1) % len(self.player_ids)]
        self.phase = GameModel.CHOOSE_BOARD_CARD_PHASE
        self.is_mask_used = False
        self.is_reform_used = False
        self.is_expand_used = False
        await self.save_to_model(game)