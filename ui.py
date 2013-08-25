import pygame, math

from pygame.locals import *
from constants import *

class UiElement(pygame.sprite.Sprite):
  def __init__(self):
    super(UiElement, self).__init__()
    self.visible = True

  def _cloneAnimations(self):
    self.animations = [i.clone() for i in self.__class__.loadedAnimations]

  loadedAnimations = None

class UiHealthBar(UiElement):
  def __init__(self, player, maxHealth, x, y):
    super(UiHealthBar, self).__init__()
    self.player = player
    self.segments = list()
    self.visible = False # This is a parent to other UI elements, managing child logic

    #Generate as many health bar segments as required, minimum two
    self.numSegments = max(2, maxHealth)

    # Only actually run this if the animations are loaded:
    if (UiHealthBarSegment.loadedAnimations is None):
      return

    #Create the top segment..
    topSegment = UiHealthBarSegment(UIHEALTHBARSEGMENT_TOP)
    topSegment.rect = UiHealthBarSegment.loadedAnimations[UIHEALTHBARSEGMENT_TOP * 2].rect.move(x,y)
    topSegmentHeight = topSegment.rect.height
    self.segments.append(topSegment)

    #Create the middle segments
    segmentHeight = UiHealthBarSegment.loadedAnimations[UIHEALTHBARSEGMENT_MIDDLE * 2].rect.height
    i = 0
    while i < ((self.numSegments - 2)):
      segment = UiHealthBarSegment(UIHEALTHBARSEGMENT_MIDDLE)
      segment.rect = UiHealthBarSegment.loadedAnimations[UIHEALTHBARSEGMENT_MIDDLE * 2].rect.move(x,y + topSegmentHeight + (segmentHeight * i))
      self.segments.append(segment)
      i = i + 1

    #Create the bottom segment
    bottomSegment = UiHealthBarSegment(UIHEALTHBARSEGMENT_BOTTOM)
    bottomSegment.rect = UiHealthBarSegment.loadedAnimations[UIHEALTHBARSEGMENT_BOTTOM * 2].rect.move(x,y + topSegmentHeight + ((self.numSegments - 2) * segmentHeight))
    self.segments.append(bottomSegment)

  def update(self):
    for segment in self.segments[self.numSegments - self.player.hp:]:
      segment.currentAnimation = (segment.segmentType * 2) + UIHEALTHBARSEGMENT_FILLED
    for segment in self.segments[0: (self.numSegments - self.player.hp)]:
      segment.currentAnimation = (segment.segmentType * 2) + UIHEALTHBARSEGMENT_UNFILLED


class UiHealthBarSegment(UiElement):
  def __init__(self, segmentType):
    super(UiHealthBarSegment, self).__init__()
    self.segmentType = segmentType
    self.currentAnimation = (segmentType * 2) + UIHEALTHBARSEGMENT_FILLED
    UiHealthBarSegment._cloneAnimations(self)