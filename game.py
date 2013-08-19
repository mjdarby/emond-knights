import pygame

from pygame.locals import *
from constants import *

class Game:
  def __init__(self):
    # Resolution.
    self.xRes = XRES
    self.yRes = YRES

    # Contains variables that are consistant across all handlers,
    # and indeed the current handler.
    self.handler = None
    # Bugfix note 2
    self.crossHandlerKeys = list()

    # PyGame variables..
    self.screen = None
    self.run = True
    self.dirtyRects = list()

    # Example variables..
    self.lives = 0
    self.score = 0
    self.currentLevelIndex = 0
    self.levelFlow = ["level01", "level02", "level03"]
    self.levelFileMap = {"level01": "data/level01.dat"} #etc
