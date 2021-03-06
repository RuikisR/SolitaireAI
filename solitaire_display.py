import pygame
from pygame.locals import *
import os
import solitaire_game
from solitaire_game import TABLEAU_OFFSET, FOUNDATION_OFFSET
import solitaire_mcts
import threading
from queue import deque


INITIAL_HEIGHT = 900
INITAL_WIDTH = 1600
GREEN = (0, 100, 0)
BLACK = (0, 0, 0)
GREY = (180, 180, 180)
MARGIN = 35
RECT_WEIGHT = 3
HIGHLIGHT_WEIGHT = 5
DATA = "assets/cards"
CARD_BACK = pygame.image.load(os.path.join(DATA, "cardBack_blue5.png"))
CARD_SIZE = CARD_BACK.get_rect().size
CARD_WIDTH = CARD_SIZE[0]
CARD_HEIGHT = CARD_SIZE[1]
AUTO_PLAY = True

pygame.init()
screen = pygame.display.set_mode((INITAL_WIDTH, INITIAL_HEIGHT))
pygame.display.set_caption("Solitaire")
clock = pygame.time.Clock()
solitaire = solitaire_game.Solitaire()
# Basic initialisation

card_images = {}  # Mapping each card to its image
for card in solitaire.deck:
    card_images[card] = pygame.image.load(
        os.path.join(DATA, f"card{card.suit_name}s{card.name}.png"))
solitaire.deal_game()

screen_sprites = {}

highlight_selection = None

move_src = None
move_dst = None
move_amount = None

calculating = False


# Displaying the cards and updating the the sprite list
def display_game(game):
    screen.fill(GREEN)
    if not game.is_game_over():
        draw_deck(game)
        draw_foundations(game)
        draw_tableaus(game)
        if highlight_selection:
            pygame.draw.rect(screen, GREY, highlight_selection,
                             HIGHLIGHT_WEIGHT)
    pygame.display.update()


def draw_deck(game):
    deck_sprite = pygame.Rect((MARGIN, MARGIN), CARD_SIZE)
    screen_sprites["deck"] = (deck_sprite, 0, 0)
    if len(game.deck) > 0:
        screen.blit(CARD_BACK, deck_sprite)
    else:
        pygame.draw.rect(screen, BLACK, deck_sprite, RECT_WEIGHT)

    waste_sprite = pygame.Rect((MARGIN * 2 + CARD_WIDTH, MARGIN), CARD_SIZE)
    screen_sprites["waste"] = (waste_sprite, 1, 0)
    if len(game.waste) > 0:
        screen.blit(card_images[game.waste.top_card()], waste_sprite)
    else:
        pygame.draw.rect(screen, BLACK, waste_sprite, RECT_WEIGHT)


def draw_foundations(game):
    for i, foundation in enumerate(game.foundations):
        sprite_x = MARGIN * (5 + i) + CARD_WIDTH * (4 + i)
        foundation_sprite = pygame.Rect((sprite_x, MARGIN), CARD_SIZE)
        screen_sprites[f"foundation({i})"] = (foundation_sprite,
                                              i + FOUNDATION_OFFSET, 0)

        if len(foundation) == 0:
            pygame.draw.rect(screen, BLACK, foundation_sprite, RECT_WEIGHT)
        else:
            screen.blit(card_images[game.foundations[i].top_card()],
                        foundation_sprite)


def draw_tableaus(game):
    for i, tableau in enumerate(game.tableaus):
        sprite_x = MARGIN * (2 + i) + CARD_WIDTH * (1 + i)

        if len(tableau) == 0:
            sprite_y = 2 * MARGIN + CARD_HEIGHT
            empty_tableau = pygame.Rect((sprite_x, sprite_y), CARD_SIZE)
            pygame.draw.rect(screen, BLACK, empty_tableau, RECT_WEIGHT)
            screen_sprites[f"empty_tableau({i})"] = (empty_tableau, i +
                                                     TABLEAU_OFFSET, 0)

        for j, card in enumerate(tableau):
            sprite_y = MARGIN * (2 + j) + CARD_HEIGHT
            tableau_sprite = None
            if card is tableau[-1]:
                tableau_sprite = pygame.Rect((sprite_x, sprite_y), CARD_SIZE)

            else:
                tableau_sprite = pygame.Rect((sprite_x, sprite_y),
                                             (CARD_WIDTH, MARGIN))

            screen_sprites[f"tableau({i}, {j})"] = (tableau_sprite,
                                                    i + TABLEAU_OFFSET, j)
            if card.hidden:
                screen.blit(CARD_BACK, tableau_sprite)
            else:
                screen.blit(card_images[card], tableau_sprite)


def highlight(selection, amount):
    global highlight_selection
    if selection[1] < TABLEAU_OFFSET or selection[1] >= FOUNDATION_OFFSET:
        highlight_selection = selection[0]
    else:
        selection_width = CARD_WIDTH
        if amount == 0:
            amount = 1
        selection_height = CARD_HEIGHT + (amount - 1) * MARGIN
        highlight_selection = pygame.Rect(selection[0].x, selection[0].y,
                                          selection_width, selection_height)


def clicked_id():
    mouse_pos = pygame.mouse.get_pos()
    for sprite in screen_sprites.values():
        if (sprite[0].collidepoint(mouse_pos)):
            return sprite


def console_input():
    print("Input a move in the form src_id, dst_id, amount")
    console_input = tuple(int(x.strip()) for x in input().split(', '))
    return console_input


def get_move(game, clicked_card):
    global move_src, move_dst, move_amount
    global highlight_selection

    if not move_src:
        move_src = clicked_card[1]
        if move_src == 0:
            move_dst = 1
            move_amount = 1
            return (move_src, move_dst, move_amount)
        elif (move_src < TABLEAU_OFFSET or move_src >= FOUNDATION_OFFSET):
            move_amount = 1
        else:
            move_amount = (len(game.tableaus[move_src - TABLEAU_OFFSET])
                           - clicked_card[2])
        highlight(clicked_card, move_amount)
    elif not move_dst:
        move_dst = clicked_card[1]
        highlight_selection = None
        if move_dst == move_src:
            quick_move(game, move_src, move_amount)
            move_src = None
            move_dst = None
            move_amount = None
        else:
            return (move_src, move_dst, move_amount)


def quick_move(game, src, amount):
    possible_moves = []
    for move in game.valid_moves:
        if move[0] == src and move[2] == amount:
            possible_moves.append(move)
    if len(possible_moves) >= 1:
        game.make_move(possible_moves[0])


def get_best_move(game):
    tree = solitaire_mcts.Solitaire_MCTS(game)
    return tree.best_move(1)


def auto_play(game, queue):
    move = solitaire_mcts.Solitaire_MCTS(solitaire).best_move(10)
    queue.append(move)
    print("Move queued")


def main():
    global screen_sprites, solitaire, move_src, move_dst
    global move_amount, highlight_selection, card_images
    global calculating
    ai = threading.Thread()
    move_q = deque()
    while(True):
        screen_sprites = {}
        display_game(solitaire)
        event = pygame.event.poll()
        game_finished = solitaire.is_game_over()
        if event.type == QUIT:
            pygame.display.quit()
            quit()
        elif event.type == MOUSEBUTTONDOWN:
            # print(f"Best move: {get_best_move(solitaire)}")
            if game_finished:
                solitaire = solitaire_game.Solitaire()
                card_images = {}  # Mapping each card to its image
                for card in solitaire.deck:
                    target = (os.path.join(
                              DATA, f"card{card.suit_name}s{card.name}.png"))
                    card_images[card] = (pygame.image.load(target))
                solitaire.deal_game()
            elif not AUTO_PLAY:
                clicked_card = clicked_id()
                move = None
                if clicked_card:
                    move = get_move(solitaire, clicked_card)
                else:
                    move_src = None
                    highlight_selection = None
                if move:
                    solitaire.make_move(move)
                    move_src = None
                    move_dst = None
                    move_amount = None
        if len(move_q) > 0 and calculating:
            solitaire.make_move(move_q.pop())
            calculating = False
        if AUTO_PLAY and not calculating:
            calculating = True
            ai = threading.Thread(target=auto_play,
                                  args=(solitaire, move_q, ),
                                  daemon=True)
            ai.start()
        clock.tick(60)


if __name__ == "__main__":
    main()
