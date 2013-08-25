import pygame

from pygame.locals import *
from constants import *

class RenderCamera(pygame.sprite.RenderPlain):
  def draw(self, surface, camera):
    # Avoid drawing things that aren't on screen. TODO: Finish the logic, it's only half done.
    for s, r in self.spritedict.items():
      # hasattr is incredibly slow, we'll get rid of it soon.
      # Note 1: Replaced by exception catching, which will be replaced itself.
      if s.visible:
        try:
          currentAnimation = s.animations[s.currentAnimation]
          surface.blit(currentAnimation.frames[s.facingRight][currentAnimation.currentFrame], s.rect.move(-s.imageXOffset - camera.x, -s.imageYOffset - camera.y))
        except AttributeError:
          try:
            if ((s.imageRect.x + s.imageRect.width) - camera.x > 0 and (s.imageRect.x < camera.x + camera.width)) \
            or (((s.imageRect.y + s.imageRect.height) - camera.y > 0) and (s.imageRect.y < camera.y + camera.height)):
              surface.blit(s.image, (s.imageRect.x - camera.x, s.imageRect.y - camera.y))
          except AttributeError:
            if ((s.rect.x + s.rect.width) - camera.x > 0 and (s.rect.x < camera.x + camera.width)) \
            or (((s.rect.y + s.rect.height) - camera.y > 0) and (s.rect.y < camera.y + camera.height)):
              surface.blit(s.image, s.rect.move(-camera.x, -camera.y))
        if DEBUG:
          pygame.draw.rect(surface, (255,255,0), s.rect.move(-camera.x, -camera.y), 1)

class RenderUi(pygame.sprite.RenderPlain):
  def draw(self, surface):
    for s, r in self.spritedict.items():
      if s.visible:
        # hasattr is incredibly slow, we'll get rid of it soon.
        # Note 1: Replaced by exception catching, which will be replaced itself.
        try:
          currentAnimation = s.animations[s.currentAnimation]
          surface.blit(currentAnimation.frames[0][currentAnimation.currentFrame], s.rect)
        except AttributeError:
          try:
            surface.blit(s.image, (s.imageRect.x, s.imageRect.y))
          except AttributeError:
            surface.blit(s.image, s.rect)
        if DEBUG:
          pygame.draw.rect(surface, (255,255,0), s.rect, 1)
