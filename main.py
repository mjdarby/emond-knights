import pygame, os, sys, copy, math
from pygame.locals import *
from threading import Thread

# Constants
main_dir = os.path.split(os.path.abspath(__file__))[0]
TILE_WIDTH = 20

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


class Player(pygame.sprite.Sprite):
  # X and Y are in pixel world co-ordinates
  def __init__(self):
    super(Player, self).__init__()
    self.xvel = 0
    self.yvel = 0
    self.xaccel = 0
    self.yaccel = 0
    self.OnGround = False
    self.image = pygame.Surface((40,60))
    self.image.fill((0,200,0))
    self.rect = self.image.get_rect()
    self.rect.topleft = (50, 50)

  def update(self, camera):
    pass#  self.rect.topleft = (self.x - camera.x, self.y - camera.y)

class Tile(pygame.sprite.Sprite):
  # X and Y are in tile world co-ordinates
  def __init__(self, x, y):
    super(Tile, self).__init__()
    self.x = x * TILE_WIDTH
    self.y = y * TILE_WIDTH
    self.image = pygame.Surface((TILE_WIDTH,TILE_WIDTH))
    self.image.fill((0,0,200))
    self.rect = self.image.get_rect()
    self.rect.topleft = (self.x, self.y)
    self.friction = 0.5

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
    self.xtiles = 50
    self.ytiles = 30
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

    # Tile stuff
    self.tilesRenderCamera = RenderCamera()
    self.tiles = dict()
    # Load level file's tiles here.
    # Testing: Create a floor of tiles
    for x in xrange(0, 50):
      for y in xrange(25, 30):
        self.tiles[(x,y)] = Tile(x,y)
        self.tilesRenderCamera.add(self.tiles[(x,y)])

    for x in xrange(20, 40):
      self.tiles[(x,x)] = Tile(x,x)
      self.tilesRenderCamera.add(self.tiles[(x,x)])      

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

    # Render each sprite using our special 'RenderCamera' groups.
    # For now, call the individual position update functions and blit manually
    self.player.update(self.camera)

    # Testing
    Game.screen.blit(self.testSurface, (400 - self.camera.x, 300 - self.camera.y))
#    Game.screen.blit(self.player.image, (self.player.rect.x - self.camera.x, self.player.rect.y - self.camera.y))
#    Game.screen.blit(self.player.image, (self.player.rect.x, self.player.rect.y))
    self.tilesRenderCamera.draw(Game.screen, self.camera)
    self.playerRenderCamera.draw(Game.screen, self.camera)
    #for tile in self.tiles:
    #  Game.screen.blit(tile.image, (tile.x - self.camera.x, tile.y - self.camera.y))

    # Show our hard work!
    pygame.display.flip()

  # def _handleKeyDown(self,event):
  #   if event.key == K_UP:
  #     self.player.yvel -= 5
  #   elif event.key == K_DOWN:
  #     self.player.yvel += 5
  #   elif event.key == K_LEFT:
  #     self.player.xvel -= 10
  #   elif event.key == K_RIGHT:
  #     self.player.xvel += 10
  #   elif event.key == K_SPACE:
  #     if self.player.onGround:
  #       self.player.yvel = -10

  # def _handleKeyUp(self, event):
  #   if event.key == K_UP:
  #     self.player.yvel += 5
  #   elif event.key == K_DOWN:
  #     self.player.yvel -= 5
  #   elif event.key == K_LEFT:
  #     self.player.xvel += 10
  #   elif event.key == K_RIGHT:
  #     self.player.xvel -= 10

  def _handleKeyDown(self,event):
    if event.key == K_LEFT:
      self.player.xaccel -= 1
    elif event.key == K_RIGHT:
      self.player.xaccel += 1
    elif event.key == K_SPACE:
      if self.player.onGround:
        self.player.yvel = -10

  def _handleKeyUp(self, event):
    if event.key == K_LEFT:
      self.player.xaccel += 1
    elif event.key == K_RIGHT:
      self.player.xaccel -= 1


  def _handleInput(self):
    for event in pygame.event.get():
        if event.type == QUIT or \
            (event.type == KEYDOWN and event.key == K_ESCAPE):
                Game.run = False
        elif event.type == KEYDOWN:
          self._handleKeyDown(event)
        elif event.type == KEYUP:
          self._handleKeyUp(event)

  def _logic_movement(self):
    # X first..
    player_rect = self.player.rect
    x_collision = False
    x_sensors = (player_rect.topleft,
      ((player_rect.midleft[0] + player_rect.topleft[0]) / 2, (player_rect.midleft[1] + player_rect.topleft[1]) / 2),
      player_rect.midleft,
      player_rect.bottomleft, 
      ((player_rect.midleft[0] + player_rect.bottomleft[0]) / 2, (player_rect.midleft[1] + player_rect.bottomleft[1]) / 2),
      player_rect.topright,
      ((player_rect.midright[0] + player_rect.topright[0]) / 2, (player_rect.midright[1] + player_rect.topright[1]) / 2),
      player_rect.midright, 
      ((player_rect.midright[0] + player_rect.bottomright[0]) / 2, (player_rect.midright[1] + player_rect.bottomright[1]) / 2),
      player_rect.bottomright)
    for sensor in x_sensors:    
      current_x = sensor[0]
      current_y = sensor[1]
      current_x_tile = current_x // TILE_WIDTH
      current_y_tile = current_y // TILE_WIDTH
      target_x = max(0, current_x + self.player.xvel)
      target_x = min(current_x + self.player.xvel, self.xpixels - self.player.rect.width)
      target_x_tile = target_x // TILE_WIDTH
      if (target_x_tile, current_y_tile) in self.tiles:
        # We've collided with something!
        tile = self.tiles[(target_x_tile, current_y_tile)]
        if math.copysign(1, self.player.xvel) > 0:
          self.player.rect.right = tile.x - 1
        else:
          self.player.rect.left = tile.x + TILE_WIDTH + 1
        x_collision = True
        break
    if not x_collision:
      self.player.rect.x += self.player.xvel

    # Y movement
    player_rect = self.player.rect
    y_collision = False
    y_sensors = (player_rect.topleft, player_rect.midtop, player_rect.topright, player_rect.bottomleft, player_rect.midbottom, player_rect.bottomright)
    for sensor in y_sensors:    
      current_x, current_y = sensor
      current_x_tile = current_x // TILE_WIDTH
      current_y_tile = current_y // TILE_WIDTH
      target_y = current_y + self.player.yvel
      target_y = max(0, current_y + self.player.yvel)
      target_y = min(current_y + self.player.yvel, self.ypixels - self.player.rect.height)
      target_y_tile = target_y // TILE_WIDTH
      if (current_x_tile, target_y_tile) in self.tiles:
        # We've collided with something!
        tile = self.tiles[(current_x_tile, target_y_tile)]
        if math.copysign(1, self.player.yvel) > 0:
          self.player.rect.bottom = tile.y - 1
          self.player.onGround = True
          # Friction adjustments, if player is not moving
          # Without the break, we might apply two frictions from two tiles. The break means only one will
          # be applied. This might seem a little odd if the blocks have different frictions.
          keys = pygame.key.get_pressed()
          if keys[K_LEFT] == keys[K_RIGHT]: # Which is to say, either neither key is pressed, or both are pressed.
            self.player.xvel -= math.copysign(min(abs(self.player.xvel), tile.friction), self.player.xvel)
        else:
          self.player.rect.top = tile.y + TILE_WIDTH + 1
          self.player.yvel = 0
        y_collision = True
        break
    if not y_collision:
      self.player.rect.y += self.player.yvel
      self.player.onGround = False

  def _logic(self):
    # Handle damage and whatnot
    
    # Gravity gonna gravitate.
    self.player.yvel += self.GRAVITY
    # Cap gravity's effect so we don't fall through things.
    self.player.yvel = min(self.player.yvel,16)
    # Movement by player.
    self.player.xvel += self.player.xaccel
    self.player.xvel = math.copysign(min(abs(self.player.xvel), 8),self.player.xvel)
    # Movement by colliding with a tile.
    # 
    # First, find the surrounding tiles we have to check against.
#    topleftTile = (int(math.floor(self.player.rect.x / TILE_WIDTH) - 1), int(math.floor(self.player.rect.y / TILE_WIDTH) - 1)) 
#    bottomrightTile = (int(math.ceil((self.player.rect.x + self.player.rect.width) / TILE_WIDTH) + 1), int(math.ceil((self.player.rect.y + self.player.rect.height) / TILE_WIDTH) + 1))
    # Check against them?!
#    for x in xrange(topleftTile[0], bottomrightTile[0]):
#      for y in xrange(topleftTile[1], bottomrightTile[1]):
#        if (x, y) in self.tiles and pygame.sprite.collide_rect(self.player, self.tiles[(x,y)]):
#          print("Collision:")
#          print((x,y))
          # Figure out the amount of dislocation required to put the player back in the right place.
    self._logic_movement()
    # Make sure the player isn't flying off the screen!

    self.player.rect.x = max(0, self.player.rect.x)
    self.player.rect.y = max(0, self.player.rect.y)
    self.player.rect.x = min(self.player.rect.x, self.xpixels - self.player.rect.width)
    self.player.rect.y = min(self.player.rect.y, self.ypixels - self.player.rect.height)


    #print(topleftTile)
    #print(bottomrightTile)


    # Handle enemy movement

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
  #Game.handler = GameScreenHandler()

  blackground = pygame.Surface(Game.screen.get_size())
  blackground = blackground.convert()
  blackground.fill((0,0,0))
  blackground.set_alpha(255)

  # Let's get in to that main loop!
  while Game.run:
    # Cap the frame rate.
    clock.tick(60)

    # For all the fading and whatnot!
    Game.screen.blit(blackground, (0,0))

    # Run the current handler, which will update the screen, etc..
    if (Game.handler == None) or not Game.handler.update():
      break

  pygame.quit()

if __name__ == "__main__":
  main()