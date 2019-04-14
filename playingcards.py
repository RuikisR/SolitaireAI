import random

SUITS = {0: "Spade", 1: "Heart", 2: "Club", 3: "Diamond"}
CARDS = {1: "Ace", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7",
            8: "8", 9: "9", 10: "10", 11: "Jack", 12: "Queen", 13: "King"}


class Card():
    def __init__(self, value, suit):
        self.value = value
        self.name = CARDS[value]
        self.suit = suit
        self.suit_name = SUITS[suit]
        self.type = self.suit % 2
        # Assumes SUIT suits alternate type eg. Black and Red
        self.hidden = True

    def is_hidden(self):
        return self.hidden

    def toggle_hidden(self):
        self.hidden = not self.is_hidden()

    def __str__(self):
        return f"{self.name} of {self.suit_name}s"

    def __repr__(self):
        return f"{self.__class__.__name__}{self.value, self.suit}"


class CardPile():
    def __init__(self):
        self.cards = []

    def draw(self):
        if len(self) > 0:
            return self.cards.pop()

    def add(self, card):
        self.cards.append(card)

    def add_pile(self, pile):
        for card in pile:
            self.cards.add(card)

    def get_top_card(self):
        if len(self.cards) > 0:
            return self.cards[-1]

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
                self.cards.append(Card(card, suit))

    def shuffle(self):
        random.shuffle(self.cards)


class Tableu(CardPile):
    # Class for game tableus
    def __init__(self):
        CardPile.__init__(self)

    def pick_up(self, amount):
        stack = []
        for card in range(amount):
            stack.append(self.cards.draw())
        return list(reversed(stack))

    def move_stack(self, tableu, amount):
        tableu.add_pile(self.cards.pick_up(amount))
