Entities
========
Entities are game objects. They differ from tiles in that they can move and have logic that can be run every frame. They come in many different varieties, for instance:
* Enemies
* Moving platforms
* Special tiles

Common functions 
-----------------
* update(): Handles entity movement, directly setting velocities, switching/advancing animations... Calls the various _logic functions.

* draw(camera): Draw the currentFrame from the currentAnimation, according to the camera and image offset. Flip the frame if facingRight is false.

* _logic(): Handles the basic logic for the entity, setting velocities, firing bullets..

* _logic_movement(): Defined in the base class, stops entities from colliding with tiles. Can be overridden by an individual class to behave different. Ultimately responsible for setting new x and y co-ordinates. Should probably be called 'resolve movement'.

* collidedWith(entity): Defines what should happen if entity hitboxes overlap. For instance:
** Player collides with Enemy: Two calls happen, first enemy.collidedWith(player), then player.collidedWith(enemy). In their collidedWith function, enemies can call 'player.damage()' and whatnot, taking care to not directly manipulate the player's attributes unless absolutely requried.

Common attributes
-----------------
* currentAnimation: An animation name.
* animations : Dictionary : A mapping of animation name to an Animation object instance.
* facingRight: Boolean used for drawing animations correctly. Will usually be true if xvel is greater than zero. When updating this, don't change it if xvel is zero.

Animations
==========
Entities can have animations. The default animations are:
* Standing
* Move Left
* Move Right
If an animation is not found in an entities animation dictionary, the standing animation is played.

Attributes
----------
* frames: A tuple (or list) of surfaces 
* currentFrame: wysiwyg
* numFrames: len(frames), just to avoid overhead of calling len(frames) constantly.
* timer: Starts at zero, increments every frame. Loops modulo delay. When it loops, the frame counter is advanced.
* delay: Delay between animation frames in game frames. Typically the delay in seconds multiplied by FPS.
* loop: The default frame to loop to after the animation has finished. If set to False, the animation does not loop.
* animate: Boolean, True if timer should advance, False otherwise.

Function
--------
* advance(): Increments self.timer. If self.timer == self.delay, set self.timer to 0, increment self.currentFrame. If self.currentFrame is now equal to self.numFrames, zero it.