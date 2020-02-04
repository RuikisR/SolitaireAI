import numpy as np
from abc import ABC, abstractmethod


class MCTS_Node(ABC):
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []

    @property
    @abstractmethod
    def untried_moves(self):
        pass

    @property
    @abstractmethod
    def gains(self):
        pass

    @property
    @abstractmethod
    def visit_count(self):
        pass

    @abstractmethod
    def expand(self):
        pass

    @abstractmethod
    def is_terminal(self):
        pass

    @abstractmethod
    def rollout(self):
        pass

    @abstractmethod
    def backpropagate(self, gain):
        pass

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def best_child(self, exploration_weight=1.4):
        print("Determining best child")
        weights = [(child.gains / child.visit_count) +
                   exploration_weight *
                   np.sqrt((2 * np.log(self.visit_count) / child.visit_count))
                   for child in self.children]
        for i, child in enumerate(self.children):
            print(f"Move: {child.move} Weight: {weights[i]}")
        return self.children[np.argmax(weights)]

    def rollout_policy(self, valid_moves):
        return valid_moves[np.random.randint(len(valid_moves))]


class MonteCarloTreeSearch(ABC):
    def __init__(self, node):
        self.root = node

    @abstractmethod
    def best_move(self, sim_number):
        pass

    def _policy(self):
        current = self.root
        while not current.is_terminal():
            if not current.is_fully_expanded():
                # print("Not fully expanded")
                return current.expand()
            else:
                current = current.best_child()
                # print("Fully expanded, returning best child")
        return current
