import pygame, os, animation

from constants import *
from pygame.locals import *

def loadImage(name, colorkey=None):
  fullpath = os.path.join(data_dir, name)
  image = pygame.image.load(fullpath)
  image = image.convert()
  if colorkey is not None:
    if colorkey is -1:
      colorkey = image.get_at((0,0))
    image.set_colorkey(colorkey, RLEACCEL)
  return image, image.get_rect()

def loadAnimation(name, width, delay, loop, colorkey=None):
  image, imageRect = loadImage(name, colorkey)
  frames = list()
  for frameNo in xrange(imageRect.width // width):
    rect = pygame.rect.Rect(frameNo*width, 0, width, imageRect.height)
    frames.append(image.subsurface(rect))
  return animation.Animation(frames, delay, loop)

def test():
  pygame.init()
  clock = pygame.time.Clock()
  screen = pygame.display.set_mode((400, 400))
  blackground = pygame.Surface(screen.get_size()).convert()
  blackground.fill((0,0,0))
  animationData = loadAnimation(data_dir+"/player_stand_run.png", 56, 0.1*FPS, 0, -1)
  while True:
    clock.tick(60)
    screen.blit(blackground, (0,0))
    screen.blit(animationData.frames[A_RIGHT_FACING][animationData.currentFrame], (0,0))
    animationData.advance()
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == QUIT or \
            (event.type == KEYDOWN and event.key == K_ESCAPE):
                return

if __name__ == "__main__":
  #profile.run('main()')
  test()