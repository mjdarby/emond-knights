import pygame, math

import loading

from pygame.locals import *
from constants import *

class Entity(pygame.sprite.Sprite):
  def __init__(self):
    super(Entity, self).__init__()
    self.xvel = 0
    self.yvel = 0
    self.maxXVel = 5
    self.xaccel = 0
    self.yaccel = 0
    self.onGround = False
    self.image = pygame.Surface((40,60))
    self.image.fill((0,200,0))
    self.rect = self.image.get_rect()
    self.rect.topleft = (50, 50)

    # Animation stuff
    self.animations = None

    # Provided the animations have been loaded, this will make a local clone for the
    # new entity
    self._cloneAnimations()

  # Calculate the new position of the entity after one frame
  def _logic_movement(self, tiles, limits):
    # Gravity gonna gravitate.
    self.yvel += GRAVITY

    # Cap speeds, so we don't fly through things!
    self.xvel = math.copysign(min(math.fabs(self.xvel), self.maxXVel),self.xvel)
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
        if math.copysign(1, self.yvel) > 0: # are we on the ground?
          self.rect.bottom = tile.y - 1
          self.onGround = True
          self.jumping = False
          # Friction adjustments, only for the the player if they are not moving
          # Without the break, we might apply two frictions from two tiles. The break means only one will
          # be applied. This might seem a little odd if the blocks have different frictions.
          if self.__class__.__name__ == "Player":
            keys = pygame.key.get_pressed()
            # Bugfix note #3
            # ... will be written why I figure out why adding 'self.hitStun' fixed the hitstun floating problem
            if (keys[K_LEFT] is keys[K_RIGHT]) or self.hitStun > 0: # Which is to say, either neither key is pressed, or both are pressed.
              if not FRICTION_ON:
                self.xvel = 0
              else:
                self.xvel -= math.copysign(min(math.fabs(self.xvel), tile.friction), self.xvel)
        else:
          self.rect.top = tile.y + TILE_WIDTH + 1
        y_collision = True
        break
    if not y_collision:
      self.rect.y += self.yvel
      if self.yvel > 0 and self.yvel < 4 and math.fabs(self.xvel) > 0.125:
        self.xvel *= 0.98
      if PERFECT_AIR_CONTROL:
        if not self.__class__.__name__ == "Player" or self.hitStun == 0: # You're falling backwards whether you like it or not if you're hit
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
    try:
      self.imageRect.topleft = (rect.x - self.imageXOffset, rect.y - self.imageYOffset)
    except AttributeError:
      pass

  # For generic entities, do nothing on each frame.
  def update(self, tiles, limits):
    pass#  self.rect.topleft = (self.x - camera.x, self.y - camera.y)

  # Helper class for animation, uses the fact that self.__class__.loadedAnimations
  # will refer to the class-specific loadedAnimations of the caller.
  # Cloned because we don't want everyone using the same animation!
  def _cloneAnimations(self):
    self.animations = [i.clone() for i in self.__class__.loadedAnimations]

  loadedAnimations = None

class Player(Entity):
  # X and Y are in pixel world co-ordinates
  def __init__(self, x, y, width, height, animations):
      super(Player, self).__init__()
      # Health and damage stuff
      self.hp = 50
      self.hitStun = 0
      self.hitInvul = 0

      # Jumping stuff
      self.jumping = False

      # Hitbox
      self.rect = pygame.rect.Rect(x, y, width, height)

      # Animation stuff
      self.imageXOffset = 10
      self.imageYOffset = 5
      self.animations = animations
      self.currentAnimation = A_STANDING
      self.facingRight = 0

      # Movement stuff
      self.maxXVel = 4

  def update(self, tiles, limits):
    # Movement and jumping stuff.
    self.xvel += self.xaccel
    self.animations[self.currentAnimation].advance()
    # Different animation behaviour depending on hitstun.
    # Need a better way of ordering/prioritising these..
    if self.hitStun == 0:
      # That is to say, don't change facing if they're standing still.
      if (self.xvel > 0):
        self.facingRight = 0
      elif (self.xvel < 0):
        self.facingRight = 1
      if not self.onGround and self.yvel > 4:
        self.currentAnimation = A_JUMPING
        self.animations[self.currentAnimation].currentFrame = 2
      elif not self.onGround and self.yvel > 0:
        self.animations[self.currentAnimation].currentFrame = 0
      elif not self.onGround and self.yvel < 0:
        self.currentAnimation = A_JUMPING
        self.animations[self.currentAnimation].currentFrame = 1
      elif (self.xvel != 0):
        self.currentAnimation = A_RUNNING
      else:
        self.currentAnimation = A_STANDING
      if self.yvel == 0:
        # If we're not moving, we can reset the jump animation.
        self.animations[A_JUMPING].currentFrame = 0
    else:
      self.currentAnimation = A_HIT      
    self._logic_movement(tiles, limits)
    # Hit stun and hit invul.
    self.hitStun -= 1
    self.hitInvul -= 1
    self.hitStun = max(0, self.hitStun)
    self.hitInvul = max(0, self.hitInvul)

  def enemyCollide(self, enemy):
    self.hp -= enemy.collisionDamage
    self.hitStun = FPS * HIT_STUN
    self.hitInvul = FPS * HIT_INVUL
    self.xvel = 5 if self.facingRight else -5 
    self.yvel = -5
    self.yaccel = 0
    self.xaccel = 0

    # Reset the hitstun animation
    self.animations[A_HIT].currentFrame = 0

def createPlayer(x, y):
  animations = [i.clone() for i in Player.loadedAnimations]
  return Player(x, y, PLAYER_WIDTH, PLAYER_HEIGHT, animations)

class PlayerBullet(Entity):
  def __init__():
    super(PlayerBullet, self).__init__()


class Enemy(Entity):
  def __init__(self):
    super(Enemy, self).__init__()
    self.image = pygame.Surface((40,40))
    self.image.fill((200,200,0))
    self.rect = self.image.get_rect()
    self.rect.topleft = (100, 100)

    self.collisionDamage = 5

  def update(self, tiles, limits):
    print "hello"
    pass

class Shazbot(Enemy):
  def __init__(self):
    super(Shazbot, self).__init__()
    self.currentAnimation = A_STANDING
    self.facingRight = 0
    self.imageRect = self.rect
    self.imageXOffset, self.imageYOffset = 0, 0
    self.moveLeft = True
    self.timer = 0

  def update(self, tiles, limits):
    if self.timer == FPS*0.5:
      self.moveLeft = not self.moveLeft
      self.timer = 0
    if self.moveLeft:
      self.xvel = -3
    else:
      self.xvel = 3
    self.timer += 1
    self.animations[self.currentAnimation].advance()

    self._logic_movement(tiles, limits)
    