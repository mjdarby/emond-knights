import pygame
import level, loading, entity

from rendercamera import *
from camera import *
from pygame.locals import *
from constants import *
from threading import Thread

from game import Game

# Helper functions
def fadeToHandler(screen, speed, destinationHander, game):
  if screen.get_alpha() > 0:
    screen.set_alpha(screen.get_alpha() - speed)
  else:
    game.crossHandlerKeys = list(pygame.key.get_pressed())
    game.handler = destinationHander

class Handler:
  # Handlers are the wrappers for the more separated parts of the game,
  # like the title screen, the main game screen, the game over..
  def update(self):
    print("Default handler")
    return True

## Loading screen stuff
def level1LoadingFunction(loadingHandler):
  # (Collidable) Tile stuff
  tiles = dict()
  # (Decorative) Tile Stuff
  decorativeTiles = dict()
  # Load the level layout. This will be moved to the loading screen.
  levelData = level.loadLevel(data_dir+"\\temp.dat")
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
  animations = (loading.loadAnimation(data_dir+"/player_stand.png", 56, 0.1*FPS, 0, -1).clone(), \
    loading.loadAnimation(data_dir+"/player_stand_run.png", 56, 0.1*FPS, 0, -1).clone(), \
    loading.loadAnimation(data_dir+"/player_jump.png", 56, 0.1*FPS, None, -1).clone(), \
    loading.loadAnimation(data_dir+"/player_hit.png", 56, 0.1*FPS, None, -1).clone()
    )
  playerData = entity.Player(50, 50, 35, 70, animations)
  
  # Enemy stuff.
  enemyData = list()
  for x in xrange(10):
    animations = (loading.loadAnimation(data_dir+"/patchy.bmp", 40, FPS//3, 0, -1).clone(),)
    enemy = entity.Shazbot()
    enemy.rect.x = x * 500
    enemyData.append(enemy)

  loadingHandler.nextHandler = GameScreenHandler(dimensions, tiles, decorativeTiles, playerData, enemyData, loadingHandler.game)

class LoadingScreenHandler(Handler):
  def __init__(self, callback, game, nextHandler=None):
    self.game = game
    # Make the background stuff here.
    background = pygame.Surface(self.game.screen.get_size())
    background = background.convert()
    background.fill((50,50,50))
    background.set_alpha(255)
    font = pygame.font.Font(None, 36)
    text = font.render("Loading, please wait!", 1, (255,255,255))
    textpos = text.get_rect(centerx=background.get_width()/2, centery=background.get_height()/2)
    background.blit(text, textpos)
    self.background = background

    # For all the fading and whatnot!
    blackground = pygame.Surface(self.game.screen.get_size())
    self.blackground = blackground.convert()
    self.blackground.fill((0,0,0))
    self.blackground.set_alpha(255)

    # Start the loading 'callback'.
    self.thread = Thread(target=callback, args=(self,))
    self.thread.start()

    self.nextHandler = nextHandler

  def _draw(self):
    self.game.screen.blit(self.blackground, (0,0))
    # Loading finished? Transition to next handler.
    if not self.thread.isAlive():
      fadeToHandler(self.background, 3, self.nextHandler, self.game)
    # Print a black screen that says 'Loading'!
    self.game.screen.blit(self.background, (0,0))

  def _handleInput(self):
    # Pump the event queue so we don't get any nasty surprises after loading.
    pygame.event.clear()

  def update(self):
    self._draw()
    self._handleInput()
    return True

## Pause Screen

class PauseScreenHandler(Handler):
  def __init__(self, returnHandler, game):
    self.game = game
    # Make the background stuff here.
    background = pygame.Surface(self.game.screen.get_size())
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
    self.game.screen.blit(self.background, (0,0))
    self.game.screen.blit(self.text, self.textpos)

    for event in pygame.event.get():
      if event.type == KEYDOWN:
        self.game.crossHandlerKeys = list(pygame.key.get_pressed())
        self.game.handler = self.returnHandler
    return True


## Menu and Title Screen stuff
class TitleScreenHandler(Handler):
  def __init__(self, buttons, game):
    self.game = game
    background = pygame.Surface(self.game.screen.get_size())
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
    self.game.screen.blit(self.background, (0,0))
    # Now draw the buttons
    for idx, button in enumerate(self.buttons):
      fontSize = 24
      if idx == self.buttonHighlighted:
        fontSize += 4
      font = pygame.font.Font(None, fontSize)
      text = font.render(button.text, 1, (255,255,255))
      textpos = text.get_rect(centerx=self.background.get_width()/2, centery=self.buttonOffset + idx * 60)
      self.game.screen.blit(text, textpos)
  def _handleInput(self):
    for event in pygame.event.get():
        if event.type == QUIT or \
            (event.type == KEYDOWN and event.key == K_ESCAPE):
                self.game.run = False
        elif event.type == KEYDOWN and event.key == K_DOWN:
          if self.buttonHighlighted + 1 < len(self.buttons):
            self.buttonHighlighted += 1
        elif event.type == KEYDOWN and event.key == K_UP:
          if self.buttonHighlighted - 1 >= 0:
            self.buttonHighlighted -= 1
        elif event.type == KEYDOWN and event.key == K_RETURN:
          self.buttons[self.buttonHighlighted].function(self.game)

  def update(self):
    self._draw()
    self._handleInput()
    return True

class GameScreenHandler(Handler):
  # The game proper, if you like. An instance of this is created for each level.
  # Contains instances for the platforms you can jump on, enemies, etc.
  # Pass in the level information and whatnot.

  def __init__(self, dimensions, tiles, decorativeTiles, playerData, enemyData, game):
    # Vital level statistics: Height and width in tiles, and in
    # pixels, for the benefit of the camera and.. everything else.
    self.game = game
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
    background = pygame.Surface(self.game.screen.get_size())
    background = background.convert()
    background.fill((135,206,235))
    self.background = background

    # Camera stuff. In reality, camera will be centered on player, rather than 'moving'.
    # That is to say, no xvel or yvel.
    self.camera = Camera(self.game.screen.get_rect())

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
    self.game.screen.blit(self.background, (0,0))

    self.decorativeTilesRenderCamera.draw(self.game.screen, self.camera)
    self.tilesRenderCamera.draw(self.game.screen, self.camera)
    self.enemyRenderCamera.draw(self.game.screen, self.camera)
    # Hack for invul blink.. Super wasteful
    if self.player.hitInvul == 0 or self.player.hitInvul % 4 == 0: # Blink every 4 frames
      self.playerRenderCamera.draw(self.game.screen, self.camera)

  def _handleKeyDown(self,event):
#    if event.key == K_LEFT:
#      self.player.xaccel -= X_ACCEL
#    elif event.key == K_RIGHT:
#      self.player.xaccel += X_ACCEL
    if event.key == K_SPACE:
      if self.player.onGround:
        self.player.jumping = True
        self.player.yvel = JUMP
    elif event.key == K_p:
      # Consider abstracting this out for all handler changes.
      # Bugfix Note 2
      events = [pygame.event.Event(KEYUP, key=idx) for (idx, key) in enumerate(pygame.key.get_pressed()) if key]
      for kEvent in events:
       self._handleKeyUp(kEvent)
      self.game.crossHandlerKeys = list(pygame.key.get_pressed())
      self.game.handler = PauseScreenHandler(self, self.game)

  def _handleKeyUp(self, event):
    if self.game.crossHandlerKeys[event.key]:
      self.game.crossHandlerKeys[event.key] = 0
      return

    #if event.key == K_LEFT:
    #  self.player.xaccel += X_ACCEL
    #elif event.key == K_RIGHT:
    #  self.player.xaccel -= X_ACCEL
    if event.key == K_SPACE:
      if self.player.jumping and self.player.yvel < -4: # Let the player cut a jump short.
        self.player.yvel = self.player.yvel/2

  def _handleInput(self):
    oldMovement = False
    # Player can't do anything under hitstun
    # TODO: Allow pausing, etc
    if self.player.hitStun == 0:
      if oldMovement:
          for event in pygame.event.get():
              if event.type == QUIT or \
                  (event.type == KEYDOWN and event.key == K_ESCAPE):
                      self.game.run = False
              elif event.type == KEYDOWN:
                self._handleKeyDown(event)
              elif event.type == KEYUP:
                self._handleKeyUp(event)
      else:
          # Handle left and right movement via keystates
          keyState = pygame.key.get_pressed()
          if keyState[K_RIGHT] and keyState[K_LEFT]:
            self.player.xaccel = 0
          elif keyState[K_LEFT]:
            self.player.xaccel = -X_ACCEL
          elif keyState[K_RIGHT]:
            self.player.xaccel = X_ACCEL
          else:
            self.player.xaccel = 0
          # Handle other input via keydown and keyup
          for event in pygame.event.get():
              if event.type == QUIT or \
                  (event.type == KEYDOWN and event.key == K_ESCAPE):
                  self.game.run = False
              elif event.type == KEYDOWN:
                self._handleKeyDown(event)
              elif event.type == KEYUP:
                self._handleKeyUp(event)

  def _logic(self):
    # Movement by player.
    self.playerRenderCamera.update(self.tiles, (self.xpixels, self.ypixels))
    # Handle enemy movement
    self.enemyRenderCamera.update(self.tiles, (self.xpixels, self.ypixels))

    # Collisions!
    # TODO: Only check against things more local to the player.
    collisions = pygame.sprite.spritecollide(self.player, self.enemyRenderCamera, False)

    if self.player.hitInvul == 0:
      for collision in collisions:
        self.player.enemyCollide(collision)

    # Adjust camera position
    self.camera.x = (self.player.rect.x + (self.player.rect.width / 2)) - (self.game.xRes / 2)
    self.camera.y = (self.player.rect.y + (self.player.rect.height / 2)) - (self.game.yRes / 2)
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