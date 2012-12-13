import pygame, os, sys, copy, math
import level, loading, entity, player
from pygame.locals import *
from threading import Thread

from constants import *

# Constants

# Asset loading functions..

# Helper functions
def fadeToHandler(screen, speed, destinationHander):
  if screen.get_alpha() > 0:
    screen.set_alpha(screen.get_alpha() - speed)
  else:
    Game.crossHandlerKeys = list(pygame.key.get_pressed())
    Game.handler = destinationHander

class Handler:
  # Handlers are the wrappers for the more separated parts of the game,
  # like the title screen, the main game screen, the game over..
  def update(self):
    print("Default handler")
    return True

## Loading screen stuff
def dummyLoadingFunction(loadingHandler):
  pass

def level1LoadingFunction(loadingHandler):
  # (Collidable) Tile stuff
  tiles = dict()
  # (Decorative) Tile Stuff
  decorativeTiles = dict()
  # Load the level layout. This will be moved to the loading screen.
  levelData = level.loadLevel(main_dir+"\\temp.dat")
  xtiles = levelData.xtiles
  ytiles = levelData.ytiles
  dimensions = (xtiles, ytiles)
  for x in xrange(levelData.xtiles):
    for y in xrange(levelData.ytiles):
      if (x,y) in levelData.tiles:
        tiles[(x,y)] = levelData.tiles[(x,y)]
      if (x,y) in levelData.decorativeTiles:
        decorativeTiles[(x,y)] = levelData.decorativeTiles[(x,y)]

  # Player stuff.
  animations = (loading.loadAnimation(data_dir+"/player_stand.png", 56, 0.1*FPS, 0, -1),)
  playerData = player.Player(50, 50, 35, 70, animations)
  
  # Enemy stuff.
  a = Shazbot()
  a.rect.x = 200
  b = Shazbot()
  b.rect.x = 300
  c = Shazbot()
  c.rect.x = 400
  enemyData = (a,b,c)

  loadingHandler.nextHandler = GameScreenHandler(dimensions, tiles, decorativeTiles, playerData, enemyData)

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

    # Start the loading 'callback'.
    self.thread = Thread(target=callback, args=(self,))
    self.thread.start()

    self.nextHandler = nextHandler

  def _draw(self):
    # Loading finished? Transition to next handler.
    if not self.thread.isAlive():
      fadeToHandler(self.background, 3, self.nextHandler)
    # Print a black screen that says 'Loading'!
    Game.screen.blit(self.background, (0,0))

  def _handleInput(self):
    # Pump the event queue so we don't get any nasty surprises after loading.
    pygame.event.clear()

  def update(self):
    self._draw()
    self._handleInput()
    return True

## Pause Screen

class PauseScreenHandler(Handler):
  def __init__(self, returnHandler):
    # Make the background stuff here.
    background = pygame.Surface(Game.screen.get_size())
    background = background.convert()
    background.fill((0,0,0))
    background.set_alpha(100)
    font = pygame.font.Font(None, 36)
    self.text = font.render("Paused, press any key to continue!", 1, (255,255,255))
    self.textpos = self.text.get_rect(centerx=background.get_width()/2, centery=background.get_height()/2)
    self.background = background
    self.returnHandler = returnHandler

  def update(self):
    self.returnHandler._draw()
    Game.screen.blit(self.background, (0,0))
    Game.screen.blit(self.text, self.textpos)

    for event in pygame.event.get():
      if event.type == KEYDOWN:
        Game.crossHandlerKeys = list(pygame.key.get_pressed())
        Game.handler = self.returnHandler
    return True


## Menu and Title Screen stuff

class Button:
  def __init__(self, text, function):
    self.text = text
    self.function = function

def quitButtonFunction():
  Game.run = False

def newButtonFunction():
  Game.crossHandlerKeys = list(pygame.key.get_pressed())
  Game.handler = LoadingScreenHandler(level1LoadingFunction)

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
    # Avoid drawing things that aren't on screen. TODO: Finish the logic, it's only half done.
    for s, r in self.spritedict.items():
      if hasattr(s, "animations"):
        currentAnimation = s.animations[s.currentAnimation]
        surface.blit(currentAnimation.frames[currentAnimation.currentFrame], s.rect.move(-s.imageXOffset - camera.x, -s.imageYOffset - camera.y))
      elif hasattr(s, "imageRect"):
        if ((s.imageRect.x + s.imageRect.width) - camera.x > 0 and (s.imageRect.x < camera.x + camera.width)) \
        or (((s.imageRect.y + s.imageRect.height) - camera.y > 0) and (s.imageRect.y < camera.y + camera.height)):
          surface.blit(s.image, (s.imageRect.x - camera.x, s.imageRect.y - camera.y))
      else:
        if ((s.rect.x + s.rect.width) - camera.x > 0 and (s.rect.x < camera.x + camera.width)) \
        or (((s.rect.y + s.rect.height) - camera.y > 0) and (s.rect.y < camera.y + camera.height)):
          surface.blit(s.image, s.rect.move(-camera.x, -camera.y))
      if DEBUG:
        pygame.draw.rect(surface, (255,255,0), s.rect.move(-camera.x, -camera.y), 1)

class Enemy(entity.Entity):
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
    self.image, self.imageRect = loading.loadImage("patchy.bmp", -1)
    self.imageRect = self.rect
    self.imageXOffset, self.imageYOffset = 0, 0
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

  def __init__(self, dimensions, tiles, decorativeTiles, playerData, enemyData):
    # Vital level statistics: Height and width in tiles, and in
    # pixels, for the benefit of the camera and.. everything else.

    # (Collidable) Tile stuff
    self.tilesRenderCamera = RenderCamera()
    self.tiles = tiles
    # (Decorative) Tile Stuff
    self.decorativeTilesRenderCamera = RenderCamera()
    self.decorativeTiles = decorativeTiles
    # Load level file's tiles here.
    self.xtiles = dimensions[0]
    self.ytiles = dimensions[1]
    # Load the level layout. This will be moved to the loading screen.
    for x in xrange(self.xtiles):
      for y in xrange(self.ytiles):
        if (x,y) in self.tiles:
          self.tilesRenderCamera.add(self.tiles[(x,y)])
        if (x,y) in self.decorativeTiles:
          self.decorativeTilesRenderCamera.add(self.decorativeTiles[(x,y)])

    # Required for keeping cameras and characters within level bounds.
    self.xpixels = self.xtiles * TILE_WIDTH
    self.ypixels = self.ytiles * TILE_WIDTH

    # Background. Right now, doesn't move and is static.
    background = pygame.Surface(Game.screen.get_size())
    background = background.convert()
    background.fill((135,206,235))
    self.background = background

    # Camera stuff. In reality, camera will be centered on player, rather than 'moving'.
    # That is to say, no xvel or yvel.
    self.camera = Camera(Game.screen.get_rect())

    # Player stuff.
    self.player = playerData
    self.playerRenderCamera = RenderCamera()
    self.playerRenderCamera.add(self.player)

    # Enemy stuff.
    self.enemyRenderCamera = RenderCamera()
    self.enemyRenderCamera.add(enemyData)

    # Update loop stuff.
    self.logicOn = True
    self.inputOn = True
    self.specialOn = False

  def _draw(self):
    # Draw the background! Let's say it never scrolls, for now.
    Game.screen.blit(self.background, (0,0))

    self.decorativeTilesRenderCamera.draw(Game.screen, self.camera)
    self.tilesRenderCamera.draw(Game.screen, self.camera)
    self.playerRenderCamera.draw(Game.screen, self.camera)
    self.enemyRenderCamera.draw(Game.screen, self.camera)

    font = pygame.font.Font(None, 16)
    text = font.render("%f"%self.player.yvel, 1, (255,255,255))
    Game.screen.blit(text, (0,0))

  def _handleKeyDown(self,event):
    if event.key == K_LEFT:
      self.player.xaccel -= X_ACCEL
    elif event.key == K_RIGHT:
      self.player.xaccel += X_ACCEL
    elif event.key == K_SPACE:
      if self.player.onGround:
        self.player.jumping = True
        self.player.yvel = JUMP
    elif event.key == K_p:
      # Consider abstracting this out for all handler changes.
      # Bugfix Note 2
      events = [pygame.event.Event(KEYUP, key=idx) for (idx, key) in enumerate(pygame.key.get_pressed()) if key]
      for kEvent in events:
       self._handleKeyUp(kEvent)
      Game.crossHandlerKeys = list(pygame.key.get_pressed())
      Game.handler = PauseScreenHandler(self)

  def _handleKeyUp(self, event):
    if Game.crossHandlerKeys[event.key]:
      Game.crossHandlerKeys[event.key] = 0
      return

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
  xRes = XRES
  yRes = YRES

  # Contains variables that are consistant across all handlers,
  # and indeed the current handler.
  handler = Handler()
  # Bugfix note 2
  crossHandlerKeys = list()
  
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

    # Show our hard work!
    pygame.display.flip()

  pygame.quit()

if __name__ == "__main__":
  main()