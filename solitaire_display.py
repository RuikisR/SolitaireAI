import pygame
from pygame.locals import *
import os
import solitaire_game
from solitaire_game import TABLEU_OFFSET, FOUNDATION_OFFSET


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
solitaire.init()

screen_sprites = {}

highlight_selection = None

move_src = None
move_dst = None
move_amount = None


# Displaying the cards and updating the the sprite list
def display_game(game):
    screen.fill(GREEN)
    draw_deck(game)
    draw_foundations(game)
    draw_tableus(game)
    if highlight_selection:
        pygame.draw.rect(screen, GREY, highlight_selection, HIGHLIGHT_WEIGHT)
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


def draw_tableus(game):
    for i, tableu in enumerate(game.tableus):
        sprite_x = MARGIN * (2 + i) + CARD_WIDTH * (1 + i)

        if len(tableu) == 0:
            sprite_y = 2 * MARGIN + CARD_HEIGHT
            empty_tableu = pygame.Rect((sprite_x, sprite_y), CARD_SIZE)
            pygame.draw.rect(screen, BLACK, empty_tableu, RECT_WEIGHT)
            screen_sprites[f"empty_tableu({i})"] = (empty_tableu, i +
                                                    TABLEU_OFFSET, 0)

        for j, card in enumerate(tableu):
            sprite_y = MARGIN * (2 + j) + CARD_HEIGHT

            if card is tableu[-1]:
                tableu_sprite = pygame.Rect((sprite_x, sprite_y), CARD_SIZE)

            else:
                tableu_sprite = pygame.Rect((sprite_x, sprite_y),
                                            (CARD_WIDTH, MARGIN))

            screen_sprites[f"tableu({i}, {j})"] = (tableu_sprite,
                                                   i + TABLEU_OFFSET, j)
            if card.hidden:
                screen.blit(CARD_BACK, tableu_sprite)
            else:
                screen.blit(card_images[card], tableu_sprite)


def highlight(selection, amount):
    global highlight_selection
    if selection[1] < TABLEU_OFFSET or selection[1] >= FOUNDATION_OFFSET:
        highlight_selection = selection[0]
    else:
        selection_width = CARD_WIDTH
        selection_height = CARD_HEIGHT + (amount - 1) * MARGIN
        highlight_selection = pygame.Rect(selection[0].x, selection[0].y,
                                          selection_width, selection_height)
        print(selection_width, selection_height)


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
        elif (move_src < TABLEU_OFFSET or move_src >= FOUNDATION_OFFSET):
            move_amount = 1
        else:
            move_amount = (len(game.tableus[move_src - TABLEU_OFFSET])
                           - clicked_card[2])
            print(move_amount)
        highlight(clicked_card, move_amount)
    elif not move_dst:
        move_dst = clicked_card[1]
        highlight_selection = None
        return (move_src, move_dst, move_amount)


if __name__ == "__main__":
    while(True):
        screen_sprites = {}
        display_game(solitaire)
        pygame.event.pump()
        event = pygame.event.wait()
        game_finished = solitaire.won
        if event.type == QUIT:
            pygame.display.quit()
            quit()
        elif event.type == MOUSEBUTTONDOWN:
            if game_finished:
                solitaire = solitaire_game.Solitaire()
                solitaire.init()
            else:
                mouse_pos = pygame.mouse.get_pos()
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
        clock.tick(60)
