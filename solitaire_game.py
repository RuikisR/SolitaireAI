from playingcards import *
import copy

TABLEAU_OFFSET = 2
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
            # Initialise each tableau as an empty card pile

        self.tableaus = []
        for tableau in range(7):
            self.tableaus.append(Tableau())
            # 7 empty tableus

        self.waste = CardPile()

        self.valid_moves = []
        # Empty pile for waste

        ''' Not Used but could be useful
        self.id_map = {0: self.deck, 1: self.waste}
        self.id_map.update((i + TABLEAU_OFFSET, tableau)
                           for i, tableau in enumerate(self.tableaus))
        self.id_map.update((i + FOUNDATION_OFFSET, foundation)
                           for i, foundation in enumerate(self.foundations))
        '''

        # Id mapping for game locations
        # 0 -> Deck
        # 1 -> Waste
        # 2-8 -> Tableaus
        # 9-12 -> Foundations

    def deal_game(self):
        for i, tableau in enumerate(self.tableaus):
            self.move_cards(self.deck, tableau, i + 1)
            tableau.top_card().toggle_hidden()
            # Calculates number of cards for each tableau and reveals top card
        self.update_valid_moves()

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

    def update_valid_moves(self):
        # Moves take the form of tuples
        # (src_id, dst_id, number_of_cards) as given in id_map
        self.valid_moves = (self.valid_deck_moves()
                            + self.valid_foundation_moves()
                            + self.valid_tableau_moves())
        if len(self.valid_moves) == 0:
            self.won = True

    def valid_deck_moves(self):
        valid_moves = []
        # Deck moves
        if len(self.deck) > 0 or len(self.waste) > 0:
            valid_moves.append((0, 1, 1))

        # Waste moves
        if len(self.waste) > 0:
            src_id = 1
            hand_card = self.waste.top_card()

            for i, tableau in enumerate(self.tableaus):
                tableau_top = tableau.top_card()
                if not tableau_top and hand_card.value == KING:
                    dst_id = i + TABLEAU_OFFSET
                    valid_moves.append((src_id, dst_id, 1))
                elif (tableau_top
                        and hand_card.type != tableau_top.type
                        and hand_card.value == tableau_top.value - 1):
                    dst_id = i + TABLEAU_OFFSET
                    valid_moves.append((src_id, dst_id, 1))
                    # Checking valid moves from waste to a tableau

            for i, foundation in enumerate(self.foundations):
                foundation_top = foundation.top_card()
                if (len(foundation) == 0 and hand_card.value == ACE
                        or (len(foundation) > 0
                            and hand_card.value == foundation_top.value + 1
                            and hand_card.suit == foundation_top.suit)):
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

                for j, tableau in enumerate(self.tableaus):
                    tableau_top = tableau.top_card()
                    if (len(tableau) > 0
                        and foundation_top.type != tableau_top.type and
                            foundation_top.value == tableau_top.value - 1):
                        dst_id = j + TABLEAU_OFFSET
                        valid_moves.append((src_id, dst_id, 1))
                        # Valid moves from foundations to tableaus
        return valid_moves

    def valid_tableau_moves(self):
        valid_moves = []
        # Tableau moves
        for i, tableau in enumerate(self.tableaus):
            if len(tableau) > 0:
                src_id = i + TABLEAU_OFFSET
                tableau_top = tableau.top_card()

                for j, foundation in enumerate(self.foundations):
                    foundation_top = foundation.top_card()
                    if (len(foundation) > 0
                            and tableau_top.suit == foundation_top.suit
                            and tableau_top.value == foundation_top.value + 1
                            or len(foundation) == 0
                            and tableau_top.value == ACE):
                        dst_id = j + FOUNDATION_OFFSET
                        valid_moves.append((src_id, dst_id, 1))
                        # Valid moves from tableau to foundation

                for j, card in enumerate(tableau):
                    if not card.hidden:
                        card_amount = len(tableau) - j
                        for k, other_tableau in enumerate(self.tableaus):
                            if i != k:
                                other_tableau_top = other_tableau.top_card()
                                if (not other_tableau_top
                                        and card.value == KING):
                                    dst_id = k + TABLEAU_OFFSET
                                    valid_moves.append(
                                        (src_id, dst_id, card_amount))
                                elif (other_tableau_top
                                        and card.type != other_tableau_top.type
                                        and card.value ==
                                        other_tableau_top.value - 1):
                                    dst_id = k + TABLEAU_OFFSET
                                    valid_moves.append(
                                        (src_id, dst_id, card_amount))
                                    # Valid tableau to tableau moves
        return valid_moves

    def make_move(self, move):
        if move in self.valid_moves:
            src_id, dst_id, amount = move
            if TABLEAU_OFFSET <= dst_id < FOUNDATION_OFFSET:
                dst = self.tableaus[dst_id - TABLEAU_OFFSET]
            elif FOUNDATION_OFFSET <= dst_id <= (FOUNDATION_OFFSET
                                                 + len(self.foundations)):
                dst = self.foundations[dst_id - FOUNDATION_OFFSET]

            if src_id == 0:
                self.draw_card()

            elif src_id == 1:
                src = self.waste
                dst.add(src.draw())

            elif TABLEAU_OFFSET <= src_id < FOUNDATION_OFFSET:
                src = self.tableaus[src_id - TABLEAU_OFFSET]
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
        self.update_valid_moves()

    def get_revealed_cards(self):
        revealed_cards = []
        revealed_cards += self.deck.get_revealed_cards()
        revealed_cards += self.waste.get_revealed_cards()
        for tableau in self.tableaus:
            revealed_cards += tableau.get_revealed_cards()
        for foundation in self.foundations:
            revealed_cards += foundation.get_revealed_cards()
        return revealed_cards

    def get_hidden_cards(self):
        hidden_cards = Deck()
        revealed_cards = self.get_revealed_cards()
        for card in revealed_cards:
            hidden_cards.pick_card(card)
        return hidden_cards

    def min_copy(self):
        instance = Solitaire()
        instance.deck = copy.deepcopy(self.deck)
        instance.waste = copy.deepcopy(self.waste)
        instance.foundations = copy.deepcopy(self.foundations)
        for i, tableau in enumerate(self.tableaus):
            for card in tableau:
                if card.is_hidden():
                    instance.tableaus[i].add(Card())
                else:
                    instance.tableaus[i].add(copy.deepcopy(card))
        return instance

    def __str__(self):
        string = "---Game Setup---\n"
        string += "\nDeck:\n"
        for card in self.deck:
            string += f"{card} - hidden: {card.is_hidden()}\n"
        string += "\nWaste:\n"
        for card in self.waste:
            string += f"{card} - hidden: {card.is_hidden()}\n"
        for index, tableau in enumerate(self.tableaus):
            string += f"\nTableau {index}:\n"
            for card in tableau:
                string += f"{card} - hidden: {card.is_hidden()}\n"
        for index, foundation in enumerate(self.foundations):
            string += f"\nFoundation {index}:\n"
            for card in foundation:
                string += f"{card} - hidden: {card.is_hidden()}\n"
        return string


# Test bench
if __name__ == "__main__":
    game = Solitaire()
    game.deal_game()
    game.draw_card()
    print(game)
    thing = game.min_copy()
    print(thing)
    print(thing.get_hidden_cards())
