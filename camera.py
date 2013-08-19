import pygame

from pygame.locals import *
from constants import *

class Camera(pygame.rect.Rect):
  def __init__(self, position):
    super(Camera, self).__init__(position)    
