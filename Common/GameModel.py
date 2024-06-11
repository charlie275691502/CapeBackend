import random

from GOAGame.models import GOAGame

class GameModel:
    def __init__(self,
                 draw_cards,
                 grave_cards,
                 board_cards_slot,
                 board_cards,
                 open_board_card_positions,
                 revealing_player_id,
                 revealing_board_card_positions,
                 player_cards,
                 player_ids,
                 taking_turn_player_id,
                 turn):
        
        self.draw_cards = draw_cards
        self.grave_cards = grave_cards
        self.board_cards_slot = board_cards_slot
        self.board_cards = board_cards
        self.open_board_card_positions = open_board_card_positions
        self.revealing_player_id = revealing_player_id
        self.revealing_board_card_positions = revealing_board_card_positions
        self.player_cards = player_cards
        self.player_ids = player_ids
        self.taking_turn_player_id = taking_turn_player_id
        self.turn = turn
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
                    player_ids,
                    player_ids[0],
                    1)
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
                   game.board.player_ids,
                   game.board.taking_turn_player_id,
                   game.board.turn)
        
    def refill_board_cards(self):
        for i in range(len(self.board_cards)) :
            if self.board_cards[i] == -1 :
                card = self.draw_one_public_card()
                self.board_cards[i] = card
    
    def draw_one_public_card(self) -> int:
        card = random.choice(self.draw_cards)
        self.draw_cards.remove(card)
        return card