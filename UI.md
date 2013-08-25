UI
==

UI elements are fixed co-ordinate elements on the game screen, displaying information about the game status, such as the player's current hitpoint total, ammo count, and level name.

Implementation
--------------
UI elements can be made up of multiple segments, controlled by the parent segment. A similar mechanism will be put in place for complicated enemy types.

HP Bars
-------
The player (and later boss) HP bars are actually made up of several segments, one for each hit point. The master hp bar item handles the child segments by calculating which ones should be turned on and off.