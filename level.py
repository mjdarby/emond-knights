import os, pygame
import struct

from constants import *

def saveLevel(level, filepath):
  binaryString = struct.pack("<hh", level.xtiles, level.ytiles)
  for x in xrange(level.xtiles):
    for y in xrange(level.ytiles):
      if (x,y) in level.tiles:
        binaryString += struct.pack("<h", level.tiles[(x,y)].tiletype)
  with open(filepath, 'wb') as f:
    f.write(binaryString)
  f.close()

def loadLevelEditor(filepath):
  with open(filepath, 'rb') as f:
    tiles = dict()
    xtiles = struct.unpack("<h", f.read(2))[0]
    ytiles = struct.unpack("<h", f.read(2))[0]
    for x in xrange(xtiles):
      for y in xrange(ytiles):
        clicked = struct.unpack("<h", f.read(2))[0]
        tiles[(x,y)] = EditorTile(x, y, clicked)
    return Level((xtiles, ytiles), tiles)

def loadLevel(filepath):
  with open(filepath, 'rb') as f:
    tiles = dict()
    xtiles = struct.unpack("<h", f.read(2))[0]
    ytiles = struct.unpack("<h", f.read(2))[0]
    for x in xrange(xtiles):
      for y in xrange(ytiles):
        clicked = struct.unpack("<h", f.read(2))[0]
        if clicked:
          tiles[(x,y)] = Tile(x, y)
    return Level((xtiles, ytiles), tiles)

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

class EditorTile(Tile):
  def __init__(self, x, y, clicked):
    super(EditorTile,self).__init__(x, y)
    self.image.fill((255,255,255))
    pygame.draw.rect(self.image, (0,0,0), self.image.get_rect(), 1)
    self.clicked = bool(clicked)
    self.tiletype = 0 if not clicked else 1

class Level:
  def __init__(self, dimensions, tiles):
    self.xtiles, self.ytiles = dimensions
    self.tiles = tiles