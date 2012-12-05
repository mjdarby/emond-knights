Level Design
============
Levels are made up of tiles. Anything that is not a tile is in the background. 
The background is drawn first, then the tiles, then any sprites.

Tiles
-----
A tile is a 20x20 sprite that may or may not be collidable with. It may deal
damage on contact, or it may provide a speed boost, or additional jumping power.

Level internals
---------------
Each level is a (.dat?) file containing a set of integers:
The first two integers determine the 'shape' of the level (width by height). The following integers
describe the level of a tile-by-tile basis, row-by-row (top-to-bottom, left-to-right). They are broken down in to
non-tile entities that should be spawned on the tile, and tile entities themselves.
* 0000 to 00FF - Tiles
* 0100 to FF00 - Entities
If a tile and entity have to share a location, they can then be XORed together in the
level file.

Example level
-------------
We'll go through this example level (with example entities), and what it does:
    0008 0005
    0000 0000 0000 0000 0000 0000 0000 0000
    0000 0000 0000 0000 0000 0000 0000 0000
    1000 0000 0000 0000 1001 0002 0001 0001
    0001 0001 0001 0001 0001 0003 0003 0003
    0003 0003 0003 0003 0003 0003 0003 0003
I've helpfully arranged the integers in a more readable fashion. In reality, they'd all be one long row of numbers.
The first two numbers describe the number of tiles in each row, and how many rows to expect.
    0008 0004
So, here we have four rows of eight tiles each. In reality, we could infer the number of
rows by dividing the remaining number of integers by the row length. We'll play it safe anyway.

Let's say 0000 is an empty space, 0001 is a floor tile which can be stepped on, 0002 is a slope,
and 0003 is a decorative tile underneath the floor. Collisions won't be checked against things you shouldn't be able to touch.
1000 is the special entity marking where the player will spawn, and 1001 marks where an enemy will spawn.