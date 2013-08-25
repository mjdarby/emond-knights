import pygame, os, sys, math
import handler, button, levels
from pygame.locals import *
from game import Game

from constants import *


## required for init
def quitButtonFunction(game):
  game.run = False

def newButtonFunction(game):
  game.crossHandlerKeys = list(pygame.key.get_pressed())
  game.handler = handler.LoadingScreenHandler(levels.level1LoadingFunction, game)

def dummyLoadingFunction(loadingHandler):
  pass

def main():
  # Initialise stuff: Pygame, the clock..
  pygame.init()
  clock = pygame.time.Clock()
  game = Game()

  # Get the PyGame variables in to Game.
  game.screen = pygame.display.set_mode((game.xRes,game.yRes), DOUBLEBUF | HWSURFACE)
  pygame.display.set_caption('Emond Knights')

  # Load the loading screen stuff, and set the handler.
  newGame = button.Button("New Game", newButtonFunction)
  exitGame = button.Button("Exit Game", quitButtonFunction)

  # For now, load directly to game
  #game.handler = handler.LoadingScreenHandler(dummyLoadingFunction, game, handler.TitleScreenHandler([newGame, exitGame], game))
  game.handler = handler.LoadingScreenHandler(levels.level1LoadingFunction, game)

  timer = 0
  # Let's get in to that main loop!
  while game.run:
    # Cap the frame rate.
    clock.tick(FPS)

    # Run the current handler, which will update the screen, etc..
    if (game.handler == None) or not game.handler.update():
      break

    # Show our hard work!
    pygame.display.flip()

    # For now, even not in DEBUG mode, print the FPS:
    if True or DEBUG:
      if timer == 60:
        timer = 0
        print clock.get_fps()
      timer += 1

  pygame.quit()


import cProfile as profile
if __name__ == "__main__":
  #profile.run('main()')
  main()