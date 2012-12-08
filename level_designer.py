import pygame, os, sys, copy, math
from pygame.locals import *
from threading import Thread

# Constants
main_dir = os.path.split(os.path.abspath(__file__))[0]
TILE_WIDTH = 20
LEVEL_WIDTH = 80
LEVEL_HEIGHT = 30
CAMERA_SPEED = 10
XRES = 800
YRES = 600

class Tile(pygame.sprite.Sprite):
  def __init__(self, x, y):
    super(Tile,self).__init__()
    self.x = x
    self.y = y
    self.clicked = False
    self.image = pygame.Surface((TILE_WIDTH, TILE_WIDTH))
    self.image.fill((255,255,255))
    pygame.draw.rect(self.image, (0,0,0), self.image.get_rect(), 1)
    self.rect = self.image.get_rect()
    self.rect.topleft = (x*TILE_WIDTH, y*TILE_WIDTH)

class RenderCamera(pygame.sprite.RenderPlain):
  def draw(self, surface, camera):
    for s, r in self.spritedict.items():
      surface.blit(s.image, (s.rect.x - camera.x, s.rect.y - camera.y))

def clicked(x, y, tiles):
  tile = tiles[(x,y)]
  tile.clicked = not tile.clicked
  if tile.clicked:
    tile.image.fill((0,0,255))
  else:
    tile.image.fill((255,255,255))
  pygame.draw.rect(tile.image, (0,0,0), tile.image.get_rect(), 1)
  return tile.clicked

def moved(x, y, tiles, fill):
  tile = tiles[(x,y)]
  tile.clicked = fill
  if tile.clicked:
    tile.image.fill((0,0,255))
  else:
    tile.image.fill((255,255,255))
  pygame.draw.rect(tile.image, (0,0,0), tile.image.get_rect(), 1)

def main():
  # Initialise stuff: Pygame, the clock..
  pygame.init()
  clock = pygame.time.Clock()
  screen = pygame.display.set_mode((XRES,YRES))
  pygame.display.set_caption('Emond Knights Level Designer')

  blackground = pygame.Surface(screen.get_size())
  blackground = blackground.convert()
  blackground.fill((255,255,255))

  camera = pygame.rect.Rect(screen.get_rect())

  tiles = dict()
  tileRenderGroup = RenderCamera()
  for x in xrange(0,LEVEL_WIDTH):
    for y in xrange(0,LEVEL_HEIGHT):
      tile = Tile(x,y)
      tiles[(x,y)] = tile
      tileRenderGroup.add(tile)

  paint = False
  fill = True

  while True:
    clock.tick(60)
    screen.blit(blackground, (0,0))
    tileRenderGroup.draw(screen, camera)
    pygame.display.flip()

    for event in pygame.event.get():
      if event.type == QUIT or \
        (event.type == KEYDOWN and event.key == K_ESCAPE):
            return
      elif event.type == MOUSEBUTTONDOWN:
        x = event.pos[0] // TILE_WIDTH
        y = event.pos[1] // TILE_WIDTH
        paint = True
        if (event.button == 1):
          fill = True
        elif (event.button == 3):
          fill = False
      elif event.type == MOUSEMOTION and paint:
        x = (event.pos[0] + camera.x) // TILE_WIDTH
        y = (event.pos[1] + camera.y) // TILE_WIDTH
        moved(x, y, tiles, fill)
      elif event.type == MOUSEBUTTONUP:
        paint = False
      elif event.type == KEYDOWN:
        if event.key == K_s:
          camera.y += CAMERA_SPEED
        elif event.key == K_w:
          camera.y -= CAMERA_SPEED
        elif event.key == K_a:
          camera.x -= CAMERA_SPEED
        elif event.key == K_d:
          camera.x += CAMERA_SPEED

    camera.x = max(0, camera.x)
    camera.y = max(0, camera.y)
    camera.x = min(camera.x, (TILE_WIDTH * LEVEL_WIDTH) - camera.width)
    camera.y = min(camera.y, (TILE_WIDTH * LEVEL_HEIGHT) - camera.height)

if __name__ == "__main__":
  main()