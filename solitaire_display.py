import pygame
from pygame.locals import *
import os
import solitaire_game

INITIAL_HEIGHT = 900
INITAL_WIDTH = 1600
GREEN = (0, 100, 0)
MARGIN = 25
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
card_images = {}
for card in solitaire.deck:
    card_images[card] = pygame.image.load(
        os.path.join(DATA, f"card{card.suit_name}s{card.name}.png"))
solitaire.init()
game_finished = False
screen_sprites = {}
solitaire.draw_card()
print(solitaire.waste.get_top_card())


def display_game(game):
    screen.fill(GREEN)

    if len(game.deck) > 0:
        deck_sprite = pygame.Rect((MARGIN, MARGIN), CARD_SIZE)
        screen_sprites["deck"] = (deck_sprite, 0)
        screen.blit(CARD_BACK, deck_sprite)

    if len(game.waste) > 0:
        waste_sprite = pygame.Rect((MARGIN * 2 + CARD_WIDTH,
                                    MARGIN), CARD_SIZE)
        screen_sprites["waste"] = (waste_sprite, 1)
        screen.blit(card_images[game.waste.get_top_card()], waste_sprite)

    pygame.display.update()


def clicked_card(sprites):
    mouse_pos = pygame.mouse.get_pos()
    for sprite in sprites.items():
        if (sprite[0].collidepoint(mouse_pos)):
            print("SUCCESS")


if __name__ == "__main__":
    while(True):
        screen_sprites = {}
        display_game(solitaire)
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
                print(f"mouse_pressed: {mouse_pos}")

        clock.tick(60)
