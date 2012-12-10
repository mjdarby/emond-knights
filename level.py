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
        tiletype = struct.unpack("<h", f.read(2))[0]
        tiles[(x,y, tiletype)] = EditorTile(x, y, tiletype)
    return Level((xtiles, ytiles), tiles)

def loadLevel(filepath):
  with open(filepath, 'rb') as f:
    tiles = dict()
    xtiles = struct.unpack("<h", f.read(2))[0]
    ytiles = struct.unpack("<h", f.read(2))[0]
    for x in xrange(xtiles):
      for y in xrange(ytiles):
        tiletype = struct.unpack("<h", f.read(2))[0]
        if tiletype == T_COLLIDABLE:
          tiles[(x,y, T_COLLIDABLE)] = CollidableTile(x, y)
        elif tiletype == T_DECORATIVE:
          tiles[(x,y, T_DECORATIVE)] = DecorativeTile(x, y)
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

class CollidableTile(Tile):
  def __init__(self, x, y):
    super(CollidableTile, self).__init__(x,y)

class DecorativeTile(Tile):
  def __init__(self, x, y):
    super(DecorativeTile, self).__init__(x,y)
    self.image.fill((200,0,200))

class EditorTile(Tile):
  def __init__(self, x, y, tiletype):
    super(EditorTile,self).__init__(x, y)
    self.image.fill((255,255,255))
    pygame.draw.rect(self.image, (0,0,0), self.image.get_rect(), 1)
    self.tiletype = tiletype

class Level:
  def __init__(self, dimensions, tiles):
    self.xtiles, self.ytiles = dimensions
    self.tiles = tiles
