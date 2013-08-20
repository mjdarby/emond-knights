import pygame
import level, loading, entity, handler

from rendercamera import *
from camera import *
from pygame.locals import *
from constants import *
from threading import Thread


# Common assets to all levels, stored in a map
# 'player' goes to the player object
# TODO: Write common load

# Level 1 Level and Assets
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
  entity.Player.loadedAnimations = (loading.loadAnimation(data_dir+"/player_stand.png", 56, 0.1*FPS, 0, -1), \
    loading.loadAnimation(data_dir+"/player_stand_run.png", 56, 0.1*FPS, 0, -1), \
    loading.loadAnimation(data_dir+"/player_jump.png", 56, 0.1*FPS, None, -1), \
    loading.loadAnimation(data_dir+"/player_hit.png", 56, 0.1*FPS, None, -1)
    )
  playerData = entity.createPlayer(50, 50)

  # Enemy stuff.
  entity.Shazbot.loadedAnimations = (loading.loadAnimation(data_dir+"/patchy.bmp", 40, FPS//3, 0, -1),)
  enemyData = list()
  for x in xrange(10):
    enemy = entity.Shazbot()
    enemy.rect.x = x * 500
    enemyData.append(enemy)

  loadingHandler.nextHandler = handler.GameScreenHandler(dimensions, tiles, decorativeTiles, playerData, enemyData, loadingHandler.game)
