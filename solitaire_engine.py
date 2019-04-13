from playingcards import *


class Solitaire():
    def __init__(self):
        self.deck = Deck()
        self.foundations = []
        for suit in SUITS:
            self.foundations.append(CardPile())
            # Initialise each tableu as an empty card pile

        self.tableus = []
        for tableu in range(7):
            self.tableus.append(Tableu())
            # 7 empty tableus

        self.deck.shuffle()
        for i, tableu in enumerate(self.tableus):
            self.move_cards(self.deck, tableu, i + 1)
            tableu.get_top_card().toggle_hidden()
            # Calculates number of cards for each tableu and reveals top card

        self.waste = CardPile()
        # Empty pile for waste

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


# Test bench
game = Solitaire()

for i in range(24):
    game.draw()
[print(card.is_hidden()) for card in game.waste]
game.reset_waste()
