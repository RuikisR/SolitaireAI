import pygame
from pygame.locals import *
import os
import solitaire_game
from solitaire_game import TABLEU_OFFSET, FOUNDATION_OFFSET


INITIAL_HEIGHT = 900
INITAL_WIDTH = 1600
GREEN = (0, 100, 0)
MARGIN = 30
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

game_finished = False
screen_sprites = {}
solitaire.draw_card()


# Displaying the cards and updating the the sprite list
def display_game(game, sprites):
    screen.fill(GREEN)

    if len(game.deck) > 0:
        deck_sprite = pygame.Rect((MARGIN, MARGIN), CARD_SIZE)
        sprites["deck"] = (deck_sprite, 0, 0)
        screen.blit(CARD_BACK, deck_sprite)

    if len(game.waste) > 0:
        waste_sprite = pygame.Rect((MARGIN * 2 + CARD_WIDTH,
                                    MARGIN), CARD_SIZE)
        sprites["waste"] = (waste_sprite, 1, 0)
        screen.blit(card_images[game.waste.top_card()], waste_sprite)

    for i, tableu in enumerate(game.tableus):
        for j, card in enumerate(tableu):
            sprite_x = MARGIN * (2 + i) + CARD_WIDTH * (1 + i)
            sprite_y = MARGIN * (2 + j) + CARD_HEIGHT

            if card is tableu[-1]:
                tableu_sprite = pygame.Rect((sprite_x, sprite_y), CARD_SIZE)

            else:
                tableu_sprite = pygame.Rect((sprite_x, sprite_y),
                                            (CARD_WIDTH, MARGIN))

            sprites[f"tableu({i}, {j})"] = (tableu_sprite, i + TABLEU_OFFSET, j)
            if card.hidden:
                screen.blit(CARD_BACK, tableu_sprite)
            else:
                screen.blit(card_images[card], tableu_sprite)

    pygame.display.update()


def clicked_id(sprites):
    mouse_pos = pygame.mouse.get_pos()
    for sprite in sprites.values():
        if (sprite[0].collidepoint(mouse_pos)):
            print(sprite)


if __name__ == "__main__":
    while(True):
        screen_sprites = {}
        display_game(solitaire, screen_sprites)
        pygame.event.pump()
        event = pygame.event.wait()
        if event.type == QUIT:
            pygame.display.quit()
            quit()
        elif event.type == MOUSEBUTTONDOWN:
            if game_finished:
                solitaire = solitaire_game.Solitaire()
                solitaire.init()
            else:
                mouse_pos = pygame.mouse.get_pos()
                clicked_card = clicked_id(screen_sprites)

        clock.tick(60)
