import pygame, math

from pygame.locals import *
from constants import *

class Entity(pygame.sprite.Sprite):
  def __init__(self):
    super(Entity, self).__init__()
    self.xvel = 0
    self.yvel = 0
    self.xaccel = 0
    self.yaccel = 0
    self.onGround = False
    self.image = pygame.Surface((40,60))
    self.image.fill((0,200,0))
    self.rect = self.image.get_rect()
    self.rect.topleft = (50, 50)

  def _logic_movement(self, tiles, limits):
    # Gravity gonna gravitate.
    self.yvel += GRAVITY

    # Cap speeds, so we don't fly through things!
    self.xvel = math.copysign(min(abs(self.xvel), 6),self.xvel)
    self.yvel = min(self.yvel,16)

    # X first..
    rect = self.rect
    x_collision = False
    x_sensors = (rect.topleft,
      ((rect.midleft[0] + rect.topleft[0]) / 2, (rect.midleft[1] + rect.topleft[1]) / 2),
      rect.midleft,
      rect.bottomleft, 
      ((rect.midleft[0] + rect.bottomleft[0]) / 2, (rect.midleft[1] + rect.bottomleft[1]) / 2),
      rect.topright,
      ((rect.midright[0] + rect.topright[0]) / 2, (rect.midright[1] + rect.topright[1]) / 2),
      rect.midright, 
      ((rect.midright[0] + rect.bottomright[0]) / 2, (rect.midright[1] + rect.bottomright[1]) / 2),
      rect.bottomright)
    for sensor in x_sensors:    
      current_x = sensor[0]
      current_y = sensor[1]
      current_x_tile = current_x // TILE_WIDTH
      current_y_tile = current_y // TILE_WIDTH
      # We don't need these, I took "Reasoning about Programming" at university,
      # and provided you can't move more pixels in one frame than there are in
      # a tile, it's all good.
      ##target_x = max(0, current_x + self.xvel)
      ##target_x = min(current_x + self.xvel, self.xpixels - self.rect.width)
      target_x = current_x + self.xvel
      target_x_tile = target_x // TILE_WIDTH
      if (target_x_tile, current_y_tile) in tiles:
        # We've collided with something!
        tile = tiles[(target_x_tile, current_y_tile)]
        if math.copysign(1, self.xvel) > 0:
          self.rect.right = tile.x - 1
        else:
          self.rect.left = tile.x + TILE_WIDTH + 1
        x_collision = True
        break
    if not x_collision:
      self.rect.x += self.xvel
    else:
      self.xvel = 0

    # Y movement
    rect = self.rect
    y_collision = False
    y_sensors = (rect.topleft, rect.midtop, rect.topright, rect.bottomleft, rect.midbottom, rect.bottomright)
    for sensor in y_sensors:    
      current_x, current_y = sensor
      current_x_tile = current_x // TILE_WIDTH
      current_y_tile = current_y // TILE_WIDTH
      #target_y = max(0, current_y + self.xvel)
      #target_y = min(current_y + self.xvel, self.ypixels - self.rect.height)
      # Bugfix note #1
      target_y = math.ceil(current_y + self.yvel) if self.yvel > 0 else current_y + self.yvel
      target_y_tile = target_y // TILE_WIDTH
      if (current_x_tile, target_y_tile) in tiles:
        # We've collided with something!
        tile = tiles[(current_x_tile, target_y_tile)]
        if math.copysign(1, self.yvel) > 0:
          self.rect.bottom = tile.y - 1
          self.onGround = True
          self.jumping = False
          # Friction adjustments, only for the the player if they are not moving
          # Without the break, we might apply two frictions from two tiles. The break means only one will
          # be applied. This might seem a little odd if the blocks have different frictions.
          if self.__class__.__name__ == "Player":
            keys = pygame.key.get_pressed()
            if keys[K_LEFT] == keys[K_RIGHT]: # Which is to say, either neither key is pressed, or both are pressed.
              if not FRICTION_ON:
                self.xvel = 0
              else:
                self.xvel -= math.copysign(min(abs(self.xvel), tile.friction), self.xvel)
        else:
          self.rect.top = tile.y + TILE_WIDTH + 1
        y_collision = True
        break
    if not y_collision:
      self.rect.y += self.yvel
      if self.yvel > 0 and self.yvel < 4 and self.xvel > 0.125:
        self.xvel *= 0.96
      if PERFECT_AIR_CONTROL:
        self.xvel = 0
      self.onGround = False
    else:
      self.yvel = 0

    # Make sure we're not flying off the screen!
    rect.x = max(0, rect.x)
    rect.y = max(0, rect.y)
    rect.x = min(rect.x, limits[0] - rect.width)
    rect.y = min(rect.y, limits[1] - rect.height)

    # Update the position of our image.
    if (hasattr(self, "imageRect")):
      self.imageRect.topleft = (rect.x - self.imageXOffset, rect.y - self.imageYOffset)

  def update(self, tiles, limits):
    pass#  self.rect.topleft = (self.x - camera.x, self.y - camera.y)