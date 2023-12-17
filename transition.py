import pygame
from settings import *

class Transition:
    def __init__(self, reset, player):

        # setup
        self.display_surface = pygame.display.get_surface()
        self.reset = reset
        self.player = player

        # overlay image, create black image, then create transparency
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color = 255
        self.speed = -2

    def play(self):
        # on every frame, the color is going to be a tiny bit darker
        self.color += self.speed
        if self.color <= 0:
            self.speed *= -1
            self.color = 0
            # call reset
            self.reset()
        if self.color > 255:
            self.color = 255
            # player wakes up after transition is over
            # set speed to -2 after transition
            self.speed = -2
            self.player.sleep = False
            
        self.image.fill((self.color, self.color, self.color))
        self.display_surface.blit(
            self.image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
