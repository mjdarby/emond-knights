Bugfix notes
=============
This file documents the longer comments on otherwise confusing bugfixes.

Bugfix Note 1
--------------
```python
target_y = math.ceil(current_y + self.yvel) if self.yvel > 0 else current_y + self.yvel
```
This line is not a nice hack: If gravity is fractional, then the player won't be moved
in to the ground on the frame after he's moved off of it! He'll be 'floating' for one frame,
with no visual effect. He won't be able to jump however. So, if we're moving towards the
ground, we assume we're going to hit the tile in the next whole pixel. This shouldn't
affect things too badly.

We can only ceil values if we're moving downwards, as otherwise jumping in to ceilings sometimes
doesn't register as we're about to enter them. If we don't catch this, we end up inside the block
in the frame of the check. This would be fine, as we'd be ejected downwards on the next frame...
Buuuut, the X direction check will fail now, and we'll get ejected to the left or right side of the
block, a bit like the old zipping glitch in Mega Man.

Nasty workaround, will come back to later for a rework.