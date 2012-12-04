import pygame, os, sys
from pygame.locals import *
from threading import Thread

# Constants
main_dir = os.path.split(os.path.abspath(__file__))[0]

# Asset loading functions..

# Helper functions
def fadeToHandler(screen, speed, destinationHander):
  if screen.get_alpha() > 0:
    screen.set_alpha(screen.get_alpha() - speed)
  else:
    Game.handler = destinationHander

class Handler:
  # Handlers are the wrappers for the more separated parts of the game,
  # like the title screen, the main game screen, the game over..
  def update(self):
    print("Default handler")
    return True

class LoadingScreenHandler(Handler):
  def __init__(self, callback, nextHandler=None):
    # Make the background stuff here.
    background = pygame.Surface(Game.screen.get_size())
    background = background.convert()
    background.fill((50,50,50))
    background.set_alpha(255)
    font = pygame.font.Font(None, 36)
    text = font.render("Loading, please wait!", 1, (255,255,255))
    textpos = text.get_rect(centerx=background.get_width()/2, centery=background.get_height()/2)
    background.blit(text, textpos)
    self.background = background

    # Start the loading callback.
    self.thread = Thread(target=callback)
    self.thread.start()

    self.nextHandler = nextHandler

  def update(self):
    # Loading finished? Transition to next handler.
    if not self.thread.isAlive():
      fadeToHandler(self.background, 3, self.nextHandler)
    # Print a black screen that says 'Loading'!
    Game.screen.blit(self.background, (0,0))
    pygame.display.flip()
    return True

class TitleScreenHandler(Handler):
  def __init__(self):
    background = pygame.Surface(Game.screen.get_size())
    background = background.convert()
    background.fill((50,50,50))
    font = pygame.font.Font(None, 36)
    text = font.render("It's the title screen!", 1, (255,255,255))
    textpos = text.get_rect(centerx=background.get_width()/2, centery=background.get_height()/2)
    background.blit(text, textpos)
    self.background = background

  def update(self):
    Game.screen.blit(self.background, (0,0))
    pygame.display.flip()
    return True

class Game:
  # Contains variables that are consistant across all handlers,
  # and indeed the current handler.
  handler = Handler()
  
  # PyGame variables..
  screen = None

  # Example variables..
  lives = 0
  score = 0

def dummy_loading():
  pygame.time.wait(2000)

def main():
  # Initialise stuff: Pygame, the clock..
  pygame.init()
  clock = pygame.time.Clock()

  # Get the PyGame variables in to Game.
  Game.screen = pygame.display.set_mode((800,600))
  pygame.display.set_caption('Emond Knights')

  # Load the loading screen stuff, and set the handler.
  Game.handler = LoadingScreenHandler(dummy_loading, TitleScreenHandler())

  # Load images inside classes..

  # Let's get in to that main loop!
  while True:
    # Cap the frame rate.
    clock.tick(60)

    # Let the player quit at any time. Remove this when all the input logic is in.
    for event in pygame.event.get():
        if event.type == QUIT or \
            (event.type == KEYDOWN and event.key == K_ESCAPE):
                return

    # For all the fading and whatnot!
    blackground = pygame.Surface(Game.screen.get_size())
    blackground = blackground.convert()
    blackground.fill((0,0,0))
    blackground.set_alpha(255)
    Game.screen.blit(blackground, (0,0))

    # Run the current handler, which will update the screen, etc..
    if (Game.handler == None) or not Game.handler.update():
      break

  pygame.quit()

if __name__ == "__main__":
  main()