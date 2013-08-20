import os

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

MARIO_MODE = False

# Megaman Mode
if not MARIO_MODE:
    X_ACCEL = 12
    PERFECT_AIR_CONTROL = True # Disables or enables impulse jumping.
    FRICTION_ON = False # For most part, anyway.
    HIT_INVUL = 1.75
    HIT_STUN = 1
# Mario Mode
else:
    X_ACCEL = 0.11
    PERFECT_AIR_CONTROL = False # Disables or enables impulse jumping.
    FRICTION_ON = True
    HIT_INVUL = 2.75
    HIT_STUN = 0.8

GRAVITY = 0.4
JUMP = -10
FPS = 60

DEBUG = False

TILE_WIDTH = 50
CAMERA_SPEED = 10
XRES = 800
YRES = 600

DISPLAY_PARAMETERS = None

T_NO_TILE = 0
T_COLLIDABLE = 1
T_DECORATIVE = 2
TILETYPES = (T_NO_TILE, T_COLLIDABLE, T_DECORATIVE)

A_STANDING = 0
A_RUNNING = 1
A_JUMPING = 2
A_HIT = 3
A_SHOOT = 4

A_RIGHT_FACING = 0
A_LEFT_FACING = 1

PLAYER_WIDTH = 35
PLAYER_HEIGHT = 70