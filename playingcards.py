import random

SUITS = {0: "Spade", 1: "Heart", 2: "Club", 3: "Diamond"}
CARDS = {1: "A", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7",
            8: "8", 9: "9", 10: "10", 11: "J", 12: "Q", 13: "K"}


class Card():
    def __init__(self, value=None, suit=None, hidden=True):
        self.value = value
        self.suit = suit
        if value is not None and suit is not None:
            self.name = CARDS[value]
            self.suit_name = SUITS[suit]
            self.type = self.suit % 2
            # Assumes SUIT suits alternate type eg. Black and Red
            self.known = True
        else:
            self.name = None
            self.suit_name = None
            self.type = None
            self.known = False
        self.hidden = hidden

    def is_hidden(self):
        return self.hidden

    def is_known(self):
        return self.known

    def make_known(self, value, suit, hidden):
        self.__init__(value, suit, hidden)

    def toggle_hidden(self):
        self.hidden = not self.is_hidden()

    def __str__(self):
        if self.value is not None and self.suit is not None:
            return f"{self.name} of {self.suit_name}s"
        else:
            return "Unknown card"

    def __repr__(self):
        return f"{self.__class__.__name__}{self.value, self.suit}"


class CardPile():
    def __init__(self):
        self.clear()

    def draw(self):
        if len(self) > 0:
            return self.cards.pop()

    def add(self, card):
        self.cards.append(card)

    def add_pile(self, pile):
        for card in pile:
            self.add(card)

    def clear(self):
        self.cards = []

    def top_card(self):
        if len(self.cards) > 0:
            return self.cards[-1]

    def get_revealed_cards(self):
        revealed_cards = []
        if len(self.cards) > 0:
            for card in self.cards:
                if not card.is_hidden():
                    revealed_cards.append(card)
        return revealed_cards

    def get_hidden_cards(self):
        hidden_cards = []
        if len(self.cards) > 0:
            for card in self.cards:
                if card.is_hidden():
                    hidden_cards.append(card)
        return hidden_cards

    def search_card(self, target_card):
        for card in self.cards:
            if (card.suit == target_card.suit and
                    card.value == target_card.value):
                self.cards.remove(card)
                if card.is_hidden():
                    card.toggle_hidden()
                return card

    def __str__(self):
        string = ""
        for card in self.cards:
            string += card.__str__() + "\n"
        return string

    def __repr__(self):
        string = ""
        for card in self.cards:
            string += card.__repr__() + "\n"
        return string

    def __len__(self):
        return len(self.cards)

    def __getitem__(self, index):
        return self.cards[index]

    def __setitem__(self, index, item):
        self.cards[index] = item

    def __reversed__(self):
        return self.cards[::-1]


class Deck(CardPile):
    def __init__(self):
        CardPile.__init__(self)
        for suit in SUITS:
            for card in CARDS:
                self.add(Card(card, suit))

    def shuffle(self):
        random.shuffle(self.cards)


class Tableau(CardPile):
    # Class for game tableaus
    def __init__(self):
        CardPile.__init__(self)

    def pick_up(self, amount):
        stack = []
        for card in range(amount):
            stack.append(self.draw())
        return list(reversed(stack))

    def move_stack(self, tableau, amount):
        tableau.add_pile(self.pick_up(amount))
        # Moves given number of cards to given tableau
