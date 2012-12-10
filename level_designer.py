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

def changeTile(x, y, tiles, fill):
  tile = tiles[(x,y)]
  tile.tiletype = fill
  if tile.tiletype == T_COLLIDABLE:
    # TODO: Draw the appropriate graphic.
    tile.image.fill((0,0,255))
  elif tile.tiletype == T_DECORATIVE:
    tile.image.fill((200,0,200))
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

  # Are we loading an old file?
  Tkinter.Tk().withdraw()
  filename = tkFileDialog.askopenfilename(filetypes=[('Level dats', '.dat')])

  levelData = dict()
  tiles = dict()
  level_width = 0
  level_height = 0

  if len(filename) > 0:
    load = True
    levelData = level.loadLevelEditor(filename)
    levelWidth = levelData.xtiles
    levelHeight = levelData.ytiles
    tiles = levelData.tiles
  else:
    load = False
    levelWidth = max(tkSimpleDialog.askinteger("Level Width", "Enter the level width in tiles (min 40):"), 40)
    levelHeight = max(tkSimpleDialog.askinteger("Level Height", "Enter the level height in tiles (min 30):"), 30)

  tileRenderGroup = RenderCamera()

  for x in xrange(0,levelWidth):
    for y in xrange(0,levelHeight):
      tile = levelData.tiles[(x,y)] if load else level.EditorTile(x,y, False)
      tiles[(x,y)] = tile
      tileRenderGroup.add(tile)
      if load: # Force a draw of all the tiles.
        changeTile(x, y, tiles, tile.tiletype)

  newLevel = level.Level((levelWidth, levelHeight), tiles)

  paint = False
  moveCamera = False
  tiletype = T_NO_TILE

  while True:
    clock.tick(60)
    screen.blit(blackground, (0,0))
    tileRenderGroup.draw(screen, camera)
    pygame.display.flip()

    for event in pygame.event.get():
      if event.type == QUIT or \
        (event.type == KEYDOWN and event.key == K_ESCAPE):
          level.saveLevel(newLevel, main_dir + "\\temp.dat")
          return
      elif event.type == MOUSEBUTTONDOWN:
        if pygame.key.get_mods() & KMOD_LSHIFT:
          moveCamera = True
        else:
          x = (event.pos[0] + camera.x) // TILE_WIDTH
          y = (event.pos[1] + camera.y) // TILE_WIDTH
          paint = True
          if (event.button == 1):
            tiletype = T_COLLIDABLE
          elif (event.button == 2):
            tiletype = T_DECORATIVE
          elif (event.button == 3):
            tiletype = T_NO_TILE
          changeTile(x, y, tiles, tiletype)
      elif event.type == MOUSEMOTION:
        if paint:
          x = (event.pos[0] + camera.x) // TILE_WIDTH
          y = (event.pos[1] + camera.y) // TILE_WIDTH
          changeTile(x, y, tiles, tiletype)
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

    camera.x = max(0, camera.x)
    camera.y = max(0, camera.y)
    camera.x = min(camera.x, (TILE_WIDTH * levelWidth) - camera.width)
    camera.y = min(camera.y, (TILE_WIDTH * levelHeight) - camera.height)

if __name__ == "__main__":
  main()