import pygame

from pygame.locals import *
from constants import *

class Animation:
  def __init__(self, frames, delay, loop):
    self.frames = list()
    self.frames.append(frames)
    self.frames.append([pygame.transform.flip(frame, True, False) for frame in frames])
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
      if self.currentFrame != self.numFrames:
        self.currentFrame += 1
      if self.currentFrame == self.numFrames and self.loop is not None:
        self.currentFrame = self.loop
      elif self.currentFrame == self.numFrames:
        self.currentFrame -= 1

  def clone(self):
    cloned = Animation([pygame.surface.Surface((1,1))], self.delay, self.loop) # So hacky, fix this one day.
    cloned.frames = self.frames
    cloned.rect = self.frames[0][0].get_rect()
    cloned.numFrames = self.numFrames
    return cloned