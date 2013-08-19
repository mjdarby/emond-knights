import pygame, os, sys, copy, math
from pygame.locals import *
from threading import Thread
import level

import Tkinter
import tkFileDialog
import tkSimpleDialog

# Constants
from constants import *

class RenderCamera(pygame.sprite.RenderPlain):
  def draw(self, surface, camera):
    for s, r in self.spritedict.items():
      surface.blit(s.image, (s.rect.x - camera.x, s.rect.y - camera.y))

def changeTile(x, y, tiles, active):
  tile = tiles[(x,y)]
  tile.active = active
  if tile.active:
    if tile.tiletype == T_COLLIDABLE:
      # TODO: Draw the appropriate graphic.
      tile.image.fill((0,0,255))
    elif tile.tiletype == T_DECORATIVE:
      tile.image.fill((200,0,200))
  else:
    tile.image.fill((255,255,255, 0))
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

  # Are we loading an old file?
  Tkinter.Tk().withdraw()
  filename = tkFileDialog.askopenfilename(filetypes=[('Level dats', '.dat')])

  levelData = dict()
  tiles = dict()
  decorativeTiles = dict()
  layers = {T_COLLIDABLE: tiles, T_DECORATIVE: decorativeTiles}
  layer = T_COLLIDABLE
  level_width = 0
  level_height = 0
  tileRenderGroup = RenderCamera()
  decorativeTileRenderGroup = RenderCamera()

  if len(filename) > 0:
    load = True
    levelData = level.loadLevelEditor(filename)
    levelWidth = levelData.xtiles
    levelHeight = levelData.ytiles
    for x in xrange(levelWidth):
      for y in xrange(levelHeight):
        tiles[(x,y)] = levelData.tiles[(x,y)]
        decorativeTiles[(x,y)] = levelData.decorativeTiles[(x,y)]
  else:
    load = False
    levelWidth = max(tkSimpleDialog.askinteger("Level Width", "Enter the level width in tiles (min {0}):".format(XRES/TILE_WIDTH)), XRES/TILE_WIDTH)
    levelHeight = max(tkSimpleDialog.askinteger("Level Height", "Enter the level height in tiles (min {0}):".format(YRES/TILE_WIDTH)), YRES/TILE_WIDTH)
    for x in xrange(levelWidth):
      for y in xrange(levelHeight):
        tile = level.EditorTile(x,y, False, T_COLLIDABLE)
        tiles[(x,y)] = tile
        decorativeTile = level.EditorTile(x, y, False, T_DECORATIVE)
        decorativeTiles[(x,y)] = decorativeTile

  for pos, tile in tiles.iteritems():
    changeTile(pos[0], pos[1], tiles, tile.active)
    tileRenderGroup.add(tile)

  for pos, decorativeTile in decorativeTiles.iteritems():
    changeTile(pos[0], pos[1], decorativeTiles, decorativeTile.active)
    decorativeTileRenderGroup.add(decorativeTile)

  newLevel = level.Level((levelWidth, levelHeight), tiles, decorativeTiles)

  paint = False
  moveCamera = False
  active = False

  while True:
    clock.tick(60)
    screen.blit(blackground, (0,0))
    decorativeTileRenderGroup.draw(screen, camera)
    tileRenderGroup.draw(screen, camera)

    pygame.display.flip()

    for event in pygame.event.get():
      if event.type == QUIT or \
        (event.type == KEYDOWN and event.key == K_ESCAPE):
          level.saveLevel(newLevel, data_dir + "\\temp.dat")
          return
      elif event.type == MOUSEBUTTONDOWN:
        if pygame.key.get_mods() & KMOD_LSHIFT:
          moveCamera = True
        else:
          x = (event.pos[0] + camera.x) // TILE_WIDTH
          y = (event.pos[1] + camera.y) // TILE_WIDTH
          paint = True
          if (event.button == 1):
            active = True
          elif (event.button == 3):
            active = False
          changeTile(x, y, layers[layer], active)
      elif event.type == MOUSEMOTION:
        if paint:
          x = (event.pos[0] + camera.x) // TILE_WIDTH
          y = (event.pos[1] + camera.y) // TILE_WIDTH
          changeTile(x, y, layers[layer], active)
        elif moveCamera:
          relX, relY = event.rel
          camera.x -= relX
          camera.y -= relY
      elif event.type == MOUSEBUTTONUP:
        paint = False
        moveCamera = False
      elif event.type == KEYDOWN:
        if event.key == K_s:
          camera.y += CAMERA_SPEED
        elif event.key == K_w:
          camera.y -= CAMERA_SPEED
        elif event.key == K_a:
          camera.x -= CAMERA_SPEED
        elif event.key == K_d:
          camera.x += CAMERA_SPEED
        elif event.key == K_1:
          layer = T_COLLIDABLE
        elif event.key == K_2:
          layer = T_DECORATIVE

    camera.x = max(0, camera.x)
    camera.y = max(0, camera.y)
    camera.x = min(camera.x, (TILE_WIDTH * levelWidth) - camera.width)
    camera.y = min(camera.y, (TILE_WIDTH * levelHeight) - camera.height)

if __name__ == "__main__":
  main()