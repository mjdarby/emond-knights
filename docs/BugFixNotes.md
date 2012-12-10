Bugfix notes
=============
This file documents the longer comments on otherwise confusing bugfixes.

Bugfix Note 1
--------------
```python
target_y = math.ceil(current_y + self.yvel) if self.yvel > 0 else current_y + self.yvel
```
This line is not a nice hack: If gravity is fractional, then the player won't be moved
in to the ground on the frame after he's prevented moving in to it. That is to say, he'll be 
'floating' for one frame, even if he's standing still on the ground. He won't be able to jump. So, 
if we're moving towards the ground, we assume we're going to hit the tile in the next whole pixel. 
This shouldn't affect things too badly.

We can only ceil values if we're moving downwards, as otherwise jumping in to ceilings sometimes
doesn't register as we're about to enter them. If we don't catch this, we end up inside the block
in the frame of the check. This would be fine, as we'd be ejected downwards on the next frame...
Buuuut, the X direction check will fail now, and we'll get ejected to the left or right side of the
block, a bit like the old zipping glitch in Mega Man.

Nasty workaround, will come back to later for a rework.

Bugfix Note 2
-------------
Before most handler changes:
```python
Game.crossHandlerKeys = list(pygame.key.get_pressed())
Game.handler = newHandler()

In every handler's _HandleKeyUp function:
```python
if Game.crossHandlerKeys[event.key]:
  Game.crossHandlerKeys[event.key] = 0
  return
```

The game to pause screen handler change (and possibly before every handler change):
```python
events = [pygame.event.Event(KEYUP, key=idx) for (idx, key) in enumerate(pygame.key.get_pressed()) if key]
for kEvent in events:
  self._handleKeyUp(kEvent)
Game.crossHandlerKeys = list(pygame.key.get_pressed())
Game.handler = PauseScreenHandler(self)
```

A prettier fix, these lines prevent any weird input things happening when switching between handlers. In the normal cases, we store what keys are being held down and change the handler. We take care to not probe the event queue until the next handler is running, otherwise weird stuff can happen (in fact, we should only probe it in the _handleInput() function, so this shouldn't be an issue). Then, the next handler will ignore any KEYUPs from keys left over
from the previous handler. 

This stops the odd case, for instance, where we pause the game, and unpause it with a movement key. The KEYDOWN reacts to the current handler's input function, switching the handler back to the game. But now the player lets go of the movement key, sending a KEYUP to the game! The player suddenly starts moving when he shouldn't. By ignoring these key-ups, the problem is solved.

However, there's another case. If we're holding down a movement key before we pause, the KEYDOWN causes us to start moving. We then pause, and let go of the movement key. The KEYUP goes to the wrong handler! After the game unpauses, the player doesn't stop moving.
If the player holds the key again before he unpauses, and continues to hold it while he unpauses, the problem is solved, and probably has the better effect of continuing the player from where he left off. Or rather, it would be, if it weren't for the previous fix, which means said keypress will be ignored. And we can't guarantee the player will hold the key anyway. So, we trigger all key-up events for held down keys before we switch handler, cancelling all movement and jumps before the handler switch.

It's not a perfect solution, because the player has to re-press a key after unpausing, but it's not unreasonable. It's on the list of things to address.