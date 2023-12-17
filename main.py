# pygame we are importing, sys we need to run the game properly
import pygame
import sys
import time
from settings import *
from level import Level

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.level = Level()

# most of the game will run inside the run method
    def run(self):

        while True:
            # checking if we are closing game
             for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

             dt = self.clock.tick(FPS) / 1000
            # always calling run method in level
             self.level.run(dt)
             pygame.display.update()

# checking if this is the main file, then creating an obj, then creating run method
if __name__ == '__main__':
    game = Game()
    game.run()
