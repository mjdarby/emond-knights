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

def moved(x, y, tiles, fill):
  tile = tiles[(x,y)]
  tile.clicked = fill
  tile.tiletype = 1 if fill else 0
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

  # Are we loading an old file?
  Tkinter.Tk().withdraw()
  filename = tkFileDialog.askopenfilename(**{'filetypes': [('Level dats', '.dat')]})

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
        moved(x, y, tiles, tile.clicked)

  newLevel = level.Level((levelWidth, levelHeight), tiles)


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
          level.saveLevel(newLevel, main_dir + "/temp.dat")
          return
      elif event.type == MOUSEBUTTONDOWN:
        x = (event.pos[0] + camera.x) // TILE_WIDTH
        y = (event.pos[1] + camera.y) // TILE_WIDTH
        paint = True
        if (event.button == 1):
          fill = True
        elif (event.button == 3):
          fill = False
        moved(x, y, tiles, fill)
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
    camera.x = min(camera.x, (TILE_WIDTH * levelWidth) - camera.width)
    camera.y = min(camera.y, (TILE_WIDTH * levelHeight) - camera.height)

if __name__ == "__main__":
  main()