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