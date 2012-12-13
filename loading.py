import pygame, os

from constants import *
from pygame.locals import *

def loadImage(name, colorkey=None):
  fullpath = os.path.join(data_dir, name)
  image = pygame.image.load(fullpath)
  image = image.convert()
  if colorkey is not None:
    if colorkey is -1:
      colorkey = image.get_at((0,0))
    image.set_colorkey(colorkey, RLEACCEL)
  return image, image.get_rect()

def loadAnimation(name, width, colorkey=None):
  image, imageRect = loadImage(name, colorkey)
  frames = list()
  for frameNo in xrange(imageRect.width // width):
    rect = pygame.rect.Rect(frameNo*width, 0, width, imageRect.height)
    frames.append(image.subsurface(rect))
  return frames, pygame.rect.Rect(0, 0, width, imageRect.height)

def test():
  pygame.init()
  clock = pygame.time.Clock()
  screen = pygame.display.set_mode((400, 400))
  frames, imageRect = loadAnimation(data_dir+"/player_stand.png", 56, -1)
  while True:
    clock.tick(60)
    screen.blit(frames[0], (0,0))
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == QUIT or \
            (event.type == KEYDOWN and event.key == K_ESCAPE):
                return
