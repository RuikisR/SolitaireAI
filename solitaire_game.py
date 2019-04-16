from playingcards import *

TABLEU_OFFSET = 2
FOUNDATION_OFFSET = 9
KING = 13
ACE = 1


class Solitaire():
    def __init__(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.won = False

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
            tableu.top_card().toggle_hidden()
            # Calculates number of cards for each tableu and reveals top card

    def draw_card(self):
        # Reveals top card of deck and places it on top of waste
        if len(self.deck) > 0:
            self.waste.add(self.deck.draw())
            self.waste.top_card().toggle_hidden()
        else:
            self.reset_waste()

    def reset_waste(self):
        # Resets the waste back to the deck
        if len(self.deck) == 0:
            for card in self.waste:
                card.toggle_hidden()
        self.deck.add_pile(reversed(self.waste))
        self.waste.clear()

    def move_cards(self, src_pile, dst_pile, amount):
        if len(src_pile) >= amount:
            for card in range(amount):
                dst_pile.add(src_pile.draw())

    def valid_moves(self):
        # Moves take the form of tuples
        # (src_id, dst_id, number_of_cards) as given in id_map
        valid_moves = (self.valid_deck_moves()
                       + self.valid_foundation_moves()
                       + self.valid_tableu_moves())
        if len(valid_moves) == 0:
            self.won = True
        return valid_moves

    def valid_deck_moves(self):
        valid_moves = []
        # Deck moves
        if len(self.deck) > 0 or len(self.waste) > 0:
            valid_moves.append((0, 1, 1))

        # Waste moves
        if len(self.waste) > 0:
            src_id = 1
            hand_card = self.waste.top_card()

            for i, tableu in enumerate(self.tableus):
                tableu_top = tableu.top_card()
                if not tableu_top and hand_card.value == KING:
                    dst_id = i + TABLEU_OFFSET
                    valid_moves.append((src_id, dst_id, 1))
                elif (tableu_top
                        and hand_card.type != tableu_top.type
                        and hand_card.value == tableu_top.value - 1):
                    dst_id = i + TABLEU_OFFSET
                    valid_moves.append((src_id, dst_id, 1))
                    # Checking valid moves from waste to a tableu

            for i, foundation in enumerate(self.foundations):
                foundation_top = foundation.top_card()
                if (len(foundation) == 0 and hand_card.value == ACE
                        or len(foundation) > 0
                        and hand_card.value == foundation_top.value + 1):
                    dst_id = i + FOUNDATION_OFFSET
                    valid_moves.append((src_id, dst_id, 1))
                    # Checking valid moves from waste to foundations
        return valid_moves

    def valid_foundation_moves(self):
        valid_moves = []
        # Foundation moves
        for i, foundation in enumerate(self.foundations):
            if len(foundation) > 0:
                src_id = i + FOUNDATION_OFFSET
                foundation_top = foundation.top_card()

                for j, tableu in enumerate(self.tableus):
                    tableu_top = tableu.top_card()
                    if (len(tableu) > 0
                        and foundation_top.type != tableu_top.type and
                            foundation_top.value == tableu_top.value - 1):
                        dst_id = j + TABLEU_OFFSET
                        valid_moves.append((src_id, dst_id, 1))
                        # Valid moves from foundations to tableus
        return valid_moves

    def valid_tableu_moves(self):
        valid_moves = []
        # Tableu moves
        for i, tableu in enumerate(self.tableus):
            if len(tableu) > 0:
                src_id = i + TABLEU_OFFSET
                tableu_top = tableu.top_card()

                for j, foundation in enumerate(self.foundations):
                    foundation_top = foundation.top_card()
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
                                other_tableu_top = other_tableu.top_card()
                                if not other_tableu_top and card.value == KING:
                                    dst_id = k + TABLEU_OFFSET
                                    valid_moves.append(
                                        (src_id, dst_id, card_amount))
                                elif (other_tableu_top
                                        and card.type != other_tableu_top.type
                                        and card.value ==
                                        other_tableu_top.value - 1):
                                    dst_id = k + TABLEU_OFFSET
                                    valid_moves.append(
                                        (src_id, dst_id, card_amount))
                                    # Valid tableu to tableu moves
        return valid_moves

    def make_move(self, move):
        if move in self.valid_moves():
            src_id, dst_id, amount = move
            if TABLEU_OFFSET <= dst_id < FOUNDATION_OFFSET:
                dst = self.tableus[dst_id - TABLEU_OFFSET]
            elif FOUNDATION_OFFSET <= dst_id <= (FOUNDATION_OFFSET
                                                 + len(self.foundations)):
                dst = self.foundations[dst_id - FOUNDATION_OFFSET]

            if src_id == 0:
                self.draw_card()

            elif src_id == 1:
                src = self.waste
                dst.add(src.draw())

            elif TABLEU_OFFSET <= src_id < FOUNDATION_OFFSET:
                src = self.tableus[src_id - TABLEU_OFFSET]
                if dst_id >= FOUNDATION_OFFSET:
                    dst.add(src.draw())
                else:
                    src.move_stack(dst, amount)
                if len(src) > 0 and src.top_card().hidden:
                    src.top_card().toggle_hidden()

            elif FOUNDATION_OFFSET <= src_id <= (FOUNDATION_OFFSET
                                                 + len(self.foundations)):
                src = self.foundations[src_id - FOUNDATION_OFFSET]
                dst.add(src.draw())


# Test bench
if __name__ == "__main__":
    game = Solitaire()
    game.init()
    game.draw_card()
    print(f"Waste: {game.waste.top_card()}")
    for i, tableu in enumerate(game.tableus):
        print(f"Tableu id {i + 2}: {tableu.top_card()}")
    print([move for move in game.valid_moves()])
