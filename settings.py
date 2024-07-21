# game options/settings
TITLE = "Rainbow Ripoff!"
TILESIZE = 36  # length in pixels
WIDTH = TILESIZE * 32  # screen width
HEIGHT = TILESIZE * 18  # screen height
FPS = 60  # frames per second
HIGHSCORE_FILE = "highscore.txt"

# mapwidth = 1152
# mapheight = 1296

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHTGREEN = (186, 254, 202)

# Player properties
FALL_VELOCITY = 7
PLAYER_WIDTH = TILESIZE
PLAYER_HEIGHT = 2 * TILESIZE

# Enemy properties
ENEMY_WIDTH = TILESIZE
ENEMY_HEIGHT = TILESIZE

BIRD_SPEED = 2
CTPLL_SPEED = 1
SPIDER_SPEED = 2

MISSILE_WIDTH = 48
MISSILE_HEIGHT = 48

# Spritesheet data
player_sprites = {
    "file_name": "Bobby_spritesR.png",
    "background": BLACK,
    "step_x": 32,  # step_x, Step_y: width, height in pixels of individual spritesheet images
    "step_y": 32,
    "image_per_row": 8}  # image_per_row: max nos of images per row

enemy_sprites = {
    "file_name": "Enemy_sprites.png",
    "background": LIGHTGREEN,
    "step_x": 32,  # step_x, Step_y: width, height in pixels of individual spritesheet images
    "step_y": 30,
    "image_per_row": 17}  # image_per_row: max nos of images per row

pick_up_sprites = {
    "file_name": "Pickup_sprites.png",
    "background": LIGHTGREEN,
    "step_x": 24,  # step_x, Step_y: width, height in pixels of individual spritesheet images
    "step_y": 24,
    "image_per_row": 16}  # image_per_row: max nos of images per row
