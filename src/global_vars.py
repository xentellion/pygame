from math import tan, pi
from pygame import Color
from src.player import Player


PLAYER: Player = None
OBJECTS = None
SPRITES = {}
WEAPONS = {}
GAME_MAP = {}


WIDTH, HEIGHT = 1200, 800
PROP = HEIGHT // 200
HALF_HEIGHT = HEIGHT // 2
TILE = 64
FPS_LOCK = 60

FOV = pi / 3
HALV_FOV = FOV / 2
MAX_DIST = 64 * TILE
RAY_COUNT = WIDTH // PROP
RAY_DELTA = FOV / RAY_COUNT
EXTRA_RAYS = RAY_COUNT // 8
LAST_EXTRA_RAY = RAY_COUNT - 1 + 2 * EXTRA_RAYS

DISTANCE = RAY_COUNT / (2 * tan(HALV_FOV))
PROJ_COEFF = PROP * DISTANCE * TILE
SCALE = WIDTH // RAY_COUNT

TEXTURE_SIDE = 64
TEXTURE_SCALE = TEXTURE_SIDE // TILE
DOUBLE_PI = 2 * pi
CENTRAL_RAY = RAY_COUNT // 2 + 1

EPSILON = 1e-6

FLOOR_COLOR = Color("#445322")
# CEILING_COLOR = Color("#8cc3d7")
# FLOOR_COLOR = Color("#717171")
CEILING_COLOR = Color("#383838")
TEXT_COLOR = Color("#FFFFFF")
RED_COLOR = Color("RED")


def mapping(a, b):
    return (
        (a // TILE) * TILE,
        (b // TILE) * TILE,
    )
