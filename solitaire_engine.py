import playingcards


class Solitaire():
    def __init__(self):
        self.deck = playingcards.Deck()
        self.foundations = []
        for suit in playingcards.SUITS:
            self.foundations.append(playingcards.CardPile())
        self.tableus = []
        for tableu in range(7):
            self.tableus.append(playingcards.Tableu())
        self.deck.shuffle()
        for i, tableu in enumerate(self.tableus):
            cards = 0
            while cards < i + 1:
                tableu.add(self.deck.draw())
                cards += 1
            tableu.get_top_card().reveal()
        self.waste = playingcards.CardPile()

    def draw(self):
        self.waste.add(self.deck.draw())
        self.waste.get_top_card().reveal()


game = Solitaire()
print(game.deck)
print(len(game.deck))
