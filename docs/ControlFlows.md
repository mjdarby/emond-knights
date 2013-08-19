Control Flow
============
The game's control flow is handled mostly by 'handlers'. A handler contains
all methods and variables pertinent to a particular context of the game. The
game loop itself calls the update function of the current handler, and handlers
can change the current handler.

For instance, before the game context is loaded, we need to load a bunch of assets,
so we have a loading context that shows an animation while a background thread
does all the loading and whatnot. Then, once the assets are loaded, the handler
can be safely switched to the game context.

Inside a handler, the update function works as most normal iterations of a game loop
do: Draw sprites, do logic.

Example Flows
-------------
Game start:
* Start up game
* Loading handler loads global assets
* Switch to title screen handler
* New game selected, create new loading screen handler for level 1
* Switch to loading handler, loads level 1 assets, creates handler for level 1
* Switch to game screen handler

Level completed:
* Player reaches end of level
* Find next level data from the Game.levels collection
* Switch to loading screen handler, load that level's assets, etc..
* Switch to game screen handler.

Game over:
* Player loses last life
* Switch to title screen handler, no loading required?

Loading a level
===============
