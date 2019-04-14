from playingcards import *

TABLEU_OFFSET = 2
FOUNDATION_OFFSET = 9
KING = 13
ACE = 1


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

        self.waste = CardPile()
        # Empty pile for waste

        self.id_map = {0: self.deck, 1: self.waste}
        self.id_map.update((i + TABLEU_OFFSET, tableu)
                           for i, tableu in enumerate(self.tableus))
        self.id_map.update((i + FOUNDATION_OFFSET, foundation)
                           for i, foundation in enumerate(self.foundations))
        # Id mapping for game locations
        # 0 -> Deck
        # 1 -> Waste
        # 2-8 -> Tableus
        # 9-12 -> Foundations

    def init(self):
        for i, tableu in enumerate(self.tableus):
            self.move_cards(self.deck, tableu, i + 1)
            tableu.get_top_card().toggle_hidden()
            # Calculates number of cards for each tableu and reveals top card

    def draw_card(self):
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
                tableu_top = tableu.get_top_card()
                if len(tableu) == 0 and hand_card.value == KING:
                    dst_id = i + TABLEU_OFFSET
                    valid_moves.append((src_id, dst_id, 1))
                elif (hand_card.type != tableu_top.type
                        and hand_card.value == tableu_top.value - 1):
                    dst_id = i + TABLEU_OFFSET
                    valid_moves.append((src_id, dst_id, 1))
                    # Checking valid moves from waste to a tableu

            for i, foundation in enumerate(self.foundations):
                foundation_top = foundation.get_top_card()
                if (len(foundation) == 0 and hand_card.value == ACE
                        or len(foundation) > 0
                        and hand_card.value == foundation_top.value + 1):
                    dst_id = i + FOUNDATION_OFFSET
                    valid_moves.append((src_id, dst_id, 1))
                    # Checking valid moves from waste to foundations

        # Foundation moves
        for i, foundation in enumerate(self.foundations):
            if len(foundation) > 0:
                src_id = i + FOUNDATION_OFFSET
                foundation_top = foundation.get_top_card()

                for j, tableu in enumerate(self.tableus):
                    tableu_top = tableu.get_top_card()
                    if (len(tableu) > 0
                        and foundation_top.type != tableu_top.type
                            and foundation_top.value == tableu_top.value - 1):
                        dst_id = j + TABLEU_OFFSET
                        valid_moves.append((src_id, dst_id, 1))
                        # Valid moves from foundations to tableus

        # Tableu moves
        for i, tableu in enumerate(self.tableus):
            if len(tableu) > 0:
                src_id = i + TABLEU_OFFSET
                tableu_top = tableu.get_top_card()

                for j, foundation in enumerate(self.foundations):
                    foundation_top = foundation.get_top_card()
                    if (len(foundation) > 0
                            and tableu_top.suit == foundation_top.suit
                            and tableu_top.value == foundation_top.value + 1
                            or len(foundation) == 0
                            and tableu_top.value == ACE):
                        dst_id = j + FOUNDATION_OFFSET
                        valid_moves.append((src_id, dst_id, 1))
                        # Valid moves from tableu to foundation

                for j, card in enumerate(tableu):
                    if not card.hidden:
                        card_amount = len(tableu) - j
                        for k, other_tableu in enumerate(self.tableus):
                            if i != k:
                                other_tableu_top = other_tableu.get_top_card()
                                if (card.type != other_tableu_top.type
                                        and card.value ==
                                        other_tableu_top.value - 1):
                                    dst_id = k + TABLEU_OFFSET
                                    valid_moves.append(
                                        (src_id, dst_id, card_amount))
                                    # Valid tableu to tableu moves

        return valid_moves


# Test bench
if __name__ == "__main__":
    game = Solitaire()
    game.draw_card()
    print(f"Waste: {game.waste.get_top_card()}")
    for i, tableu in enumerate(game.tableus):
        print(f"Tableu id {i + 2}: {tableu.get_top_card()}")
    print([move for move in game.get_valid_moves()])
