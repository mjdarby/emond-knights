import os, pygame
import struct

from constants import *

def saveLevel(level, filepath):
  binaryString = struct.pack("<hh", level.xtiles, level.ytiles)
  for x in xrange(level.xtiles):
    for y in xrange(level.ytiles):
      if (x,y) in level.tiles:
        binaryString += struct.pack("<h", level.tiles[(x,y)].active)
  for x in xrange(level.xtiles):
    for y in xrange(level.ytiles):
      if (x,y) in level.decorativeTiles:
        binaryString += struct.pack("<h", level.decorativeTiles[(x,y)].active)
  with open(filepath, 'wb') as f:
    f.write(binaryString)
  f.close()

def loadLevelEditor(filepath):
  with open(filepath, 'rb') as f:
    tiles = dict()
    decorativeTiles = dict()
    xtiles = struct.unpack("<h", f.read(2))[0]
    ytiles = struct.unpack("<h", f.read(2))[0]
    for x in xrange(xtiles):
      for y in xrange(ytiles):
        active = struct.unpack("<h", f.read(2))[0]
        tiles[(x, y)] = EditorTile(x, y, active, T_COLLIDABLE)
    for x in xrange(xtiles):
      for y in xrange(ytiles):
        active = struct.unpack("<h", f.read(2))[0]
        decorativeTiles[(x, y)] = EditorTile(x, y, active, T_DECORATIVE)    
    return Level((xtiles, ytiles), tiles, decorativeTiles)

def loadLevel(filepath):
  with open(filepath, 'rb') as f:
    tiles = dict()
    decorativeTiles = dict()
    xtiles = struct.unpack("<h", f.read(2))[0]
    ytiles = struct.unpack("<h", f.read(2))[0]
    for x in xrange(xtiles):
      for y in xrange(ytiles):
        active = struct.unpack("<h", f.read(2))[0]
        if active:
          tiles[(x, y)] = CollidableTile(x, y)
    for x in xrange(xtiles):
      for y in xrange(ytiles):
        active = struct.unpack("<h", f.read(2))[0]
        if active:
          decorativeTiles[(x, y)] = DecorativeTile(x, y)
    return Level((xtiles, ytiles), tiles, decorativeTiles)

class Tile(pygame.sprite.Sprite):
  # X and Y are in tile world co-ordinates
  def __init__(self, x, y):
    super(Tile, self).__init__()
    self.x = x * TILE_WIDTH
    self.y = y * TILE_WIDTH
    self.image = pygame.Surface((TILE_WIDTH,TILE_WIDTH))
    self.image = self.image.convert()
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
  def __init__(self, x, y, active, tiletype):
    super(EditorTile,self).__init__(x, y)
    self.image = pygame.Surface((TILE_WIDTH, TILE_WIDTH))
    self.image = self.image.convert_alpha()
    self.image.fill((255,255,255, 0))
    pygame.draw.rect(self.image, (0,0,0), self.image.get_rect(), 1)
    self.active = active
    self.tiletype = tiletype

class Level:
  def __init__(self, dimensions, tiles, decorativeTiles):
    self.xtiles, self.ytiles = dimensions
    self.tiles = tiles
    self.decorativeTiles = decorativeTiles
