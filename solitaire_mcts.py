from solitaire_game import Solitaire, TABLEAU_OFFSET
from playingcards import *
import mcts
import copy
from numpy import random, argmax


class Solitaire_Copy(Solitaire):
    def __init__(self, game):
        Solitaire.__init__(self)
        for i, tableau in enumerate(game.tableaus):
            for card in tableau:
                if card.is_hidden():
                    self.tableaus[i].add(Card())
                else:
                    revealed = self.deck.search_card(card)
                    self.tableaus[i].add(revealed)
        for i, foundation in enumerate(game.foundations):
            for card in foundation:
                self.foundations[i].add(self.deck.search_card(card))
        for card in game.waste:
            self.waste.add(self.deck.search_card(card))
        self.missing_cards = self.deck
        self.deck = CardPile()
        for card in game.deck:
            self.deck.add(self.missing_cards.search_card(card))
        self.move_counter = game.move_counter

    def make_move(self, move):
        next_states = []
        if (2 <= move[0] <= 8 and
                len(self.tableaus[move[0] - TABLEAU_OFFSET]) > 1):
            for card in self.missing_cards:
                clone = copy.deepcopy(self)
                Solitaire.make_move(clone, move)
                tableau = clone.tableaus[move[0] - TABLEAU_OFFSET]
                if len(tableau) > 0 and not tableau[-1].is_known():
                    tableau[-1] = clone.missing_cards.search_card(card)
                next_states.append(clone)
        else:
            clone = copy.deepcopy(self)
            Solitaire.make_move(clone, move)
            next_states.append(clone)
        return next_states

    def __str__(self):
        string = Solitaire.__str__(self)
        string += "\nMissing Cards:\n"
        for card in self.missing_cards:
            string += f"{card} - hidden: {card.is_hidden()}\n"
        return string


class Solitaire_MCTS_Node(mcts.MCTS_Node):
    def __init__(self, state, parent=None, move=None):
        mcts.MCTS_Node.__init__(self, state, parent)
        self._visit_count = 0
        self._results = 0
        self._untried_moves = None
        self.move = move

    @property
    def untried_moves(self):
        if self._untried_moves is None:
            self._untried_moves = self.state.valid_moves
        return self._untried_moves

    @property
    def gains(self):
        return self._results

    @property
    def visit_count(self):
        return self._visit_count

    def expand(self):
        '''
        # print("Expanding node")
        move = self._untried_moves.pop()
        next_states = self.state.make_move(move)
        # print(next_states)
        child_nodes = [Solitaire_MCTS_Node(state, self, move)
                       for state in next_states]
        gains = [len(self.state.valid_moves) - len(child.state.valid_moves)
                 for child in child_nodes]
        print(gains)
        ideal_child = child_nodes[argmax(gains)]
        self.children.append(ideal_child)
        return ideal_child
        '''

    def is_terminal(self):
        return self.state.is_game_over()

    def rollout(self):
        '''
        current = self.state
        while not current.is_game_over():
            possible_moves = current.valid_moves
            move = self.rollout_policy(possible_moves)
            current = current.make_move(move)
            rand_i = random.randint(len(current))
            current = current[rand_i]
        return len(current.missing_cards)
        '''

    def backpropagate(self, reward):
        self._visit_count += 1
        self._results += 0
        if self.parent:
            self.parent.backpropagate(reward)


class Solitaire_MCTS(mcts.MonteCarloTreeSearch):
    def __init__(self, game):
        root = Solitaire_MCTS_Node(Solitaire_Copy(game))
        mcts.MonteCarloTreeSearch.__init__(self, root)
