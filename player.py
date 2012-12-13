import pygame, entity, loading

from pygame.locals import *
from constants import *

class Player(entity.Entity):
  # X and Y are in pixel world co-ordinates
  # def __init__(self):
  #   super(Player, self).__init__()
  #   self.jumping = False
  #   self.image = pygame.Surface((40,60))
  #   self.image.fill((0,200,0))
  #   self.image, self.imageRect = loading.loadImage("testSprite.bmp", -1)
  #   self.imageXOffset = 10
  #   self.imageYOffset = 10
  #   self.rect = pygame.rect.Rect(50, 50, 35, 70)

  def __init__(self, x, y, width, height, animations):
     super(Player, self).__init__()
     self.jumping = False
     self.image, self.imageRect = loading.loadImage("testSprite.bmp", -1)
     self.imageXOffset = 10
     self.imageYOffset = 10
     self.rect = pygame.rect.Rect(x, y, width, height)
     self.animations = animations
     self.currentAnimation = A_STANDING

  def _logic_animation(self):
    pass

  def update(self, tiles, limits):
    self.xvel += self.xaccel
    self.animations[self.currentAnimation].advance()
    self._logic_movement(tiles, limits)