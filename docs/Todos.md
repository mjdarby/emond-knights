To-dos
======

Global
------
* Error checking (should probably be doing this as I go along)

Level designer
--------------
* Add capability to add different types of tiles: Physical, background, damaging
* Need an interface for said tiles!

Game Screen
-----------
* Backgrounds
* Tiles
* Entities
* Collision detection
* Scrolling backgrounds

Loading Screen
--------------
* Pretty-ifictation

Title Screen
------------
* Buttons (New Game, Quit, etc.)
* Pretty-ification

Bugs?
-----
* Touching the edge of a level won't reset the corresponding velocity. Consider 'ghost tiles' around the level.
* Funky camera when jumping near top of level
* Pausing while moving requires the player to press the movement key again after unpausing.

Bugs
----
* Pressing and holding a key before pausing means they keyup event may not reach the game handler.
** To fix, trigger all key-up events on pause.