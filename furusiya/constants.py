SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

# size of the map
MAP_WIDTH = 80
MAP_HEIGHT = 43

# sizes and coordinates relevant for the GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1
INVENTORY_WIDTH = 50

# parameters for dungeon generator
# TODO: move into dungeon generator
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
NUM_TREES = 1800
MAX_ROOM_MONSTERS = 3
MAX_ROOM_ITEMS = 2

# spell values
HEAL_AMOUNT = 4
LIGHTNING_DAMAGE = 20
LIGHTNING_RANGE = 5
CONFUSE_RANGE = 8
CONFUSE_NUM_TURNS = 10
FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 12

FOV_ALGO = 'BASIC'
FOV_LIGHT_WALLS = True

LIMIT_FPS = 20  # 20 frames-per-second maximum

color_dark_ground = (32, 32, 32)
color_dark_wall = (48, 48, 48)
color_light_ground = (128, 128, 128)
color_light_wall = (192, 192, 192)

GROUND_CHARACTER = '.'
TREE_CHARACTER = '#'
