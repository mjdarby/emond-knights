import pygame

from pygame.locals import *
from constants import *

class Animation:
  def __init__(self, frames, delay, loop):
    self.frames = frames
    self.rect = frames[0].get_rect()
    self.numFrames = len(frames)
    self.delay = delay
    self.loop = loop
    self.currentFrame = 0
    self.timer = 0
    self.animate = True

  def advance(self):
    self.timer += 1
    if self.timer == self.delay:
      self.timer = 0
      self.currentFrame += 1
      if self.currentFrame == self.numFrames:
        self.currentFrame = 0

  def clone(self):
    return Animation(self.frames, self.delay, self.loop)