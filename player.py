import pygame, entity, loading

from pygame.locals import *
from constants import *

class Player(entity.Entity):
  # X and Y are in pixel world co-ordinates
  def __init__(self, x, y, width, height, animations):
     super(Player, self).__init__()
     self.jumping = False
     self.image, self.imageRect = loading.loadImage("testSprite.bmp", -1)
     self.imageXOffset = 10
     self.imageYOffset = 5
     self.rect = pygame.rect.Rect(x, y, width, height)
     self.animations = animations
     self.currentAnimation = A_STANDING
     self.facingRight = 0

  def _logic_animation(self):
    pass

  def update(self, tiles, limits):
    self.xvel += self.xaccel
    # That is to say, don't change facing if they're standing still.
    if (self.xvel > 0):
      self.facingRight = 0
    elif (self.xvel < 0):
      self.facingRight = 1
    self.animations[self.currentAnimation].advance()
    if not self.onGround:
      self.currentAnimation = A_JUMPING
    elif (self.xvel != 0):
      self.currentAnimation = A_RUNNING
    else:
      self.currentAnimation = A_STANDING
    if self.yvel == 0:
      # If we're not moving, we can reset the jump animation.
      self.animations[A_JUMPING].currentFrame = 0
    self._logic_movement(tiles, limits)