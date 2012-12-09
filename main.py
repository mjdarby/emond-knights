import pygame, os, sys, copy, math, level
from pygame.locals import *
from threading import Thread

# Constants
main_dir = os.path.split(os.path.abspath(__file__))[0]
TILE_WIDTH = 20
X_ACCEL = 0.5
PERFECT_AIR_CONTROL = False # Disables or enables impulse jumping.
GRAVITY = 0.4
JUMP = -10
FPS = 60

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

## Loading screen stuff
def dummyLoadingFunction():
  pass

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
    # Pump the event queue so we don't get any nasty surprises after loading.
    pygame.event.clear()
    return True

## Menu and Title Screen stuff

class Button:
  def __init__(self, text, function):
    self.text = text
    self.function = function

def quitButtonFunction():
  Game.run = False

def newButtonFunction():
  Game.handler = GameScreenHandler()

class TitleScreenHandler(Handler):
  def __init__(self, buttons):
    background = pygame.Surface(Game.screen.get_size())
    background = background.convert()
    background.fill((50,50,50))
    font = pygame.font.Font(None, 36)
    text = font.render("Emond Knights", 1, (255,255,255))
    textpos = text.get_rect(centerx=background.get_width()/2, centery=background.get_height()/4)
    background.blit(text, textpos)
    self.background = background
    self.buttons = buttons[:]
    self.buttonHighlighted = 0
    self.buttonOffset = background.get_height() / 2

  def _draw(self):
    # Draw the background..
    Game.screen.blit(self.background, (0,0))
    # Now draw the buttons
    for idx, button in enumerate(self.buttons):
      fontSize = 24
      if idx == self.buttonHighlighted:
        fontSize += 4
      font = pygame.font.Font(None, fontSize)
      text = font.render(button.text, 1, (255,255,255))
      textpos = text.get_rect(centerx=self.background.get_width()/2, centery=self.buttonOffset + idx * 60)
      Game.screen.blit(text, textpos)
    # Handle any button presses here: Navigating menu, quitting game, selecting things.
    pygame.display.flip()

  def _handleInput(self):
    for event in pygame.event.get():
        if event.type == QUIT or \
            (event.type == KEYDOWN and event.key == K_ESCAPE):
                Game.run = False
        elif event.type == KEYDOWN and event.key == K_DOWN:
          if self.buttonHighlighted + 1 < len(self.buttons):
            self.buttonHighlighted += 1
        elif event.type == KEYDOWN and event.key == K_UP:
          if self.buttonHighlighted - 1 >= 0:
            self.buttonHighlighted -= 1
        elif event.type == KEYDOWN and event.key == K_RETURN:
          self.buttons[self.buttonHighlighted].function()

  def update(self):
    self._draw()
    self._handleInput()
    return True

## Game stuff
class RenderCamera(pygame.sprite.RenderPlain):
  def draw(self, surface, camera):
    for s, r in self.spritedict.items():
      surface.blit(s.image, (s.rect.x - camera.x, s.rect.y - camera.y))

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
    self.xvel = math.copysign(min(abs(self.xvel), 8),self.xvel)
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

  def update(self, tiles, limits):
    pass#  self.rect.topleft = (self.x - camera.x, self.y - camera.y)


class Player(Entity):
  # X and Y are in pixel world co-ordinates
  def __init__(self):
    super(Player, self).__init__()
    self.jumping = False

  def update(self, tiles, limits):
    self.xvel += self.xaccel
    self._logic_movement(tiles, limits)

class Enemy(Entity):
  def __init__(self):
    super(Enemy, self).__init__()
    self.image = pygame.Surface((40,40))
    self.image.fill((200,200,0))
    self.rect = self.image.get_rect()
    self.rect.topleft = (100, 100)

  def update(self, tiles, limits):
    print "hello"
    pass

class Shazbot(Enemy):
  def __init__(self):
    super(Shazbot, self).__init__()
    self.moveLeft = True
    self.timer = 0

  def update(self, tiles, limits):
    if self.timer == FPS*0.5:
      self.moveLeft = not self.moveLeft
      self.timer = 0
    if self.moveLeft:
      self.xvel = -5
    else:
      self.xvel = 5
    self.timer += 1

    self._logic_movement(tiles, limits)

class Camera(pygame.rect.Rect):
  def __init__(self, position):
    super(Camera, self).__init__(position)    

class GameScreenHandler(Handler):
  # The game proper, if you like. An instance of this is created for each level.
  # Contains instances for the platforms you can jump on, enemies, etc.
  # Pass in the level information and whatnot.

  # Game constants!
  GRAVITY = 0.5

  def __init__(self):
    # Vital level statistics: Height and width in tiles, and in
    # pixels, for the benefit of the camera and.. everything else.

    # Tile stuff
    self.tilesRenderCamera = RenderCamera()
    self.tiles = dict()
    # Load level file's tiles here.
    load = True
    self.xtiles = 50
    self.ytiles = 30
    if not load:
      # Testing: Create a floor of tiles
      for x in xrange(0, 50):
        for y in xrange(25, 30):
          self.tiles[(x,y)] = level.Tile(x,y)
          self.tilesRenderCamera.add(self.tiles[(x,y)])
    else:
      # Load the level layout. This will be moved to the loading screen.
      levelData = level.loadLevel(main_dir+"\\temp.dat")
      self.xtiles = levelData.xtiles
      self.ytiles = levelData.ytiles
      for x in xrange(levelData.xtiles):
        for y in xrange(levelData.ytiles):
          if (x,y) in levelData.tiles:
            self.tiles[(x,y)] = levelData.tiles[(x,y)]
            self.tilesRenderCamera.add(self.tiles[(x,y)])

    self.xpixels = self.xtiles * TILE_WIDTH
    self.ypixels = self.ytiles * TILE_WIDTH

    # Background. Right now, doesn't move and is static.
    background = pygame.Surface(Game.screen.get_size())
    background = background.convert()
    background.fill((50,50,50))
    self.background = background

    # Camera stuff. In reality, camera will be centered on player, rather than 'moving'.
    # That is to say, no xvel or yvel.
    self.camera = Camera(Game.screen.get_rect())

    # Player stuff.
    self.player = Player()
    self.playerRenderCamera = RenderCamera()
    self.playerRenderCamera.add(self.player)

    # Enemy stuff.
    self.enemy = Shazbot()
    self.enemyRenderCamera = RenderCamera()
    self.enemyRenderCamera.add(self.enemy)
    a = Shazbot()
    a.rect.x = 200
    b = Shazbot()
    b.rect.x = 300
    c = Shazbot()
    c.rect.x = 400
    self.enemyRenderCamera.add((a,b,c))

    # Update loop stuff.
    self.logicOn = True
    self.inputOn = True
    self.specialOn = False

    self.testSurface = pygame.Surface((100,100))
    self.testSurface = self.testSurface.convert()
    self.testSurface.fill((200,0,0))

  def _draw(self):
    # Draw the background! Let's say it never scrolls, for now.
    Game.screen.blit(self.background, (0,0))

    # Testing
    Game.screen.blit(self.testSurface, (400 - self.camera.x, 300 - self.camera.y))
#    Game.screen.blit(self.player.image, (self.player.rect.x - self.camera.x, self.player.rect.y - self.camera.y))
#    Game.screen.blit(self.player.image, (self.player.rect.x, self.player.rect.y))
    self.tilesRenderCamera.draw(Game.screen, self.camera)
    self.playerRenderCamera.draw(Game.screen, self.camera)
    self.enemyRenderCamera.draw(Game.screen, self.camera)

    font = pygame.font.Font(None, 16)
    text = font.render("%f"%self.player.yvel, 1, (255,255,255))
    Game.screen.blit(text, (0,0))

    # Show our hard work!
    pygame.display.flip()

  def _handleKeyDown(self,event):
    if event.key == K_LEFT:
      self.player.xaccel -= X_ACCEL
    elif event.key == K_RIGHT:
      self.player.xaccel += X_ACCEL
    elif event.key == K_SPACE:
      if self.player.onGround:
        self.player.jumping = True
        self.player.yvel = JUMP

  def _handleKeyUp(self, event):
    if event.key == K_LEFT:
      self.player.xaccel += X_ACCEL
    elif event.key == K_RIGHT:
      self.player.xaccel -= X_ACCEL
    elif event.key == K_SPACE:
      if self.player.jumping and self.player.yvel < -4: # Let the player cut a jump short.
        self.player.yvel = self.player.yvel/2


  def _handleInput(self):
    for event in pygame.event.get():
        if event.type == QUIT or \
            (event.type == KEYDOWN and event.key == K_ESCAPE):
                Game.run = False
        elif event.type == KEYDOWN:
          self._handleKeyDown(event)
        elif event.type == KEYUP:
          self._handleKeyUp(event)

  def _logic(self):
    # Movement by player.
    self.playerRenderCamera.update(self.tiles, (self.xpixels, self.ypixels))
    # Handle enemy movement
    self.enemyRenderCamera.update(self.tiles, (self.xpixels, self.ypixels))

    # Adjust camera position
    self.camera.x = (self.player.rect.x + (self.player.rect.width / 2)) - (Game.xRes / 2)
    self.camera.y = (self.player.rect.y + (self.player.rect.height / 2)) - (Game.yRes / 2)
    self.camera.x = max(0, self.camera.x)
    self.camera.y = max(0, self.camera.y)
    self.camera.x = min(self.camera.x, self.xpixels - self.camera.width)
    self.camera.y = min(self.camera.y, self.ypixels - self.camera.height)

  def _special(self):
    pass

  def update(self):
    self._draw()
    if self.inputOn:
      self._handleInput()
    if self.logicOn:
      self._logic()
    if self.specialOn:
      self._special()
    return True

class Game:
  # Resolution.
  xRes = 800
  yRes = 600

  # Contains variables that are consistant across all handlers,
  # and indeed the current handler.
  handler = Handler()
  
  # PyGame variables..
  screen = None
  run = True

  # Example variables..
  lives = 0
  score = 0
  currentLevelIndex = 0
  levelFlow = ["level01", "level02", "level03"]
  levelFileMap = {"level01": "data/level01.dat"} #etc

def main():
  # Initialise stuff: Pygame, the clock..
  pygame.init()
  clock = pygame.time.Clock()

  # Get the PyGame variables in to Game.
  Game.screen = pygame.display.set_mode((Game.xRes,Game.yRes))
  pygame.display.set_caption('Emond Knights')

  # Load the loading screen stuff, and set the handler.
  newGame = Button("New Game", newButtonFunction)
  exitGame = Button("Exit Game", quitButtonFunction)
  Game.handler = LoadingScreenHandler(dummyLoadingFunction, TitleScreenHandler([newGame, exitGame]))

  blackground = pygame.Surface(Game.screen.get_size())
  blackground = blackground.convert()
  blackground.fill((0,0,0))
  blackground.set_alpha(255)

  # Let's get in to that main loop!
  while Game.run:
    # Cap the frame rate.
    clock.tick(FPS)

    # For all the fading and whatnot!
    Game.screen.blit(blackground, (0,0))

    # Run the current handler, which will update the screen, etc..
    if (Game.handler == None) or not Game.handler.update():
      break

  pygame.quit()

if __name__ == "__main__":
  main()