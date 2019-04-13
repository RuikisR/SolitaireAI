from playingcards import *


class Solitaire():
    def __init__(self):
        self.deck = Deck()
        self.deck.shuffle()

        self.foundations = []
        for suit in SUITS:
            self.foundations.append(CardPile())
            # Initialise each tableu as an empty card pile

        self.tableus = []
        for tableu in range(7):
            self.tableus.append(Tableu())
            # 7 empty tableus

        for i, tableu in enumerate(self.tableus):
            self.move_cards(self.deck, tableu, i + 1)
            tableu.get_top_card().toggle_hidden()
            # Calculates number of cards for each tableu and reveals top card

        self.waste = CardPile()
        # Empty pile for waste

        self.id_map = {0: self.deck, 1: self.waste}
        self.id_map.update((i + 2, tableu)
                           for i, tableu in enumerate(self.tableus))
        self.id_map.update((i + 8, foundation)
                           for i, foundation in enumerate(self.foundations))
        # Id mapping for game locations
        # 0 -> Deck
        # 1 -> Waste
        # 2-7 -> Tableus
        # 8-11 -> Foundations

    def draw(self):
        # Reveals top card of deck and places it on top of waste
        self.waste.add(self.deck.draw())
        self.waste.get_top_card().toggle_hidden()

    def reset_waste(self):
        # Resets the waste back to the deck
        if len(self.deck) == 0:
            for card in self.waste:
                card.toggle_hidden()
            self.move_cards(self.waste, self.deck, len(self.waste))

    def move_cards(self, src_pile, dst_pile, amount):
        if len(src_pile) >= amount:
            for card in range(amount):
                dst_pile.add(src_pile.draw())

    def get_valid_moves(self):
        # Moves take the form of tuples
        # (src_id, dst_id, number_of_cards) as given in id_map
        valid_moves = []

        # Deck moves
        if len(self.deck) > 0:
            valid_moves.append((0, 1, 1))
            # If deck is not empty, drawing a card to waste is valid
        elif len(self.waste) > 0:
            valid_moves.append((1, 0, 0))
            # Special case allowing for resetting of waste back to deck

        # Waste moves
        if len(self.waste) > 0:
            src_id = 1
            hand_card = self.waste.get_top_card()

            for i, tableu in enumerate(self.tableus):
                dst_id = i + 2
                tableu_top = tableu.get_top_card()
                if len(tableu) == 0 and hand_card.value == 13:
                    valid_moves.append((src_id, dst_id, 1))
                elif (hand_card.type != tableu_top.type
                        and hand_card.value == tableu_top.value - 1):
                    valid_moves.append((src_id, dst_id, 1))
                    # Checking valid moves from waste to a tableu

            for i, foundation in enumerate(self.foundations):
                dst_id = i + 8
                foundation_top = foundation.get_top_card()
                if (len(foundation) == 0 and hand_card.value == 1
                        or len(foundation) > 0
                        and hand_card.value == foundation_top.value + 1):
                    valid_moves.append((src_id, dst_id, 1))
                    # Checking valid moves from waste to foundations

        return valid_moves


# Test bench
game = Solitaire()
game.draw()
print(f"Waste: {game.waste.get_top_card()}")
for i, tableu in enumerate(game.tableus):
    print(f"Tableu id {i + 2}: {tableu.get_top_card()}")
print([move for move in game.get_valid_moves()])
