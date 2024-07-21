# KidsCanCode - Game Development with Pygame video series
# Jumpy! (a platform game) - Part 1
# Video link: https://www.youtube.com/watch?v=uWvb3QzA48c
# Project setup
import pygame 
import random
from settings import *
from sprites import *
from spritesheet_functions import *
from os import path

# TO DO
# Invunerability powerup
# Fix player falling through platforms whilst dying when jump key pressed
# Enemy hit points

class Camera:

    def __init__(self, game):

        self.rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        self.game = game

    def update(self, target):
        # update camera offset according to player's new position
        x_offset = -target.rect.centerx + int(WIDTH / 2)  # player moves right, map moves left relative to camera.  Add half screen width to keep player centred on screen
        y_offset = -target.rect.centery + int(HEIGHT / 2)  # player moves up, map moves down ""            ""

        # limit scrolling to map size
        x_offset = min(0, x_offset)  # left map edge
        y_offset = min(0, y_offset)  # top map edge
        x_offset = max(-(self.game.map.width - WIDTH), x_offset)  # right map edge
        y_offset = max(-(self.game.map.height - HEIGHT), y_offset)  # bottom map edge

        # reposition camera rect
        self.rect.x = x_offset
        self.rect.y = y_offset

    def apply(self, entity):
        # move on screen objects according to camera offset e.g. player moves right, map objects shift left
        return entity.rect.move(self.rect.topleft)


class Map:

    def __init__(self, filename):
        self.data = []
        with open(filename, 'rt') as f:
            for line in f:
                line = line.replace("\t", '')  # remove tab scape characters
                self.data.append(line.strip())  # .strip prevents invisible new line characters being read from text file

        self.width = len(self.data[0]) * TILESIZE  # pixel width of the map
        self.height = len(self.data) * TILESIZE


class Game:

    def __init__(self):
        # initialize game window, etc
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.camera = Camera(self)

        self.clock = pygame.time.Clock()
        self.elapsed_time = 0
        self.dt = 0  # time for 1 mainloop
        self.running = True  # in game

        # animation images
        self.player_animations = {"idle": {"L": [], "R": [], "T": 1},
                                  "walk": {"L": [], "R": [], "T": 0.25},
                                  "jump": {"L": [], "R": [], "T": 1},
                                  "fall": {"L": [], "R": [], "T": 0.5},
                                  "die": {"L": [], "R": [], "T": 1}}  # init empty dictionary

        self.ctpll_animations = {"walk": {"L": [], "R": [], "T": 0.5}}  # caterpillar animations
        self.bird_animations = {"fly": {"L": [], "R": [], "T": 0.3}}  # bird animations
        self.spider_animations = {"walk": {"L": [], "R": [], "T": 0.3},
                                  "climb": {"L": [], "R": [], "T": 0.3}}  # spider animations
        self.missile_animations = {"fly": {"L": [], "R": [], "T": 1},
                                   "explode": {"L": [], "R": [], "T": 0.5}}
        self.load_data()

    def load_data(self):

        self.dir = "C:\\Users\\ben_s\\Documents\\Python_Scripts\\Pygame_Templates\\Platformer_nophysics"
        self.map = Map(path.join(self.dir, 'map.txt'))  # create map object from Map class, tilemap.py

        with open(path.join(self.dir, HIGHSCORE_FILE), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0

        # background image
        self.background = pygame.image.load(path.join("Images", "Background.png")).convert()

        # load spritesheets
        self.player_spritesheet = SpriteSheet(player_sprites)
        self.enemy_spritesheet = SpriteSheet(enemy_sprites)
        self.pickup_spritesheet = SpriteSheet(pick_up_sprites)

        # load images
        self.pltf_image = pygame.image.load(path.join("Images", "platform_tile.png")).convert()
        self.pltf_image = pygame.transform.scale(self.pltf_image, (TILESIZE, TILESIZE))  # fit platform tile image to TILESIZE
        self.pick_up_images = self.pickup_spritesheet.load_animation(0, 1, TILESIZE, TILESIZE, 32)  # list containing all pick_up images
        self.speedboost_image = self.pickup_spritesheet.get_image(288, 0, pick_up_sprites["step_x"], pick_up_sprites["step_y"], 2 * TILESIZE, 2 * TILESIZE)
        self.jumpboost_image = self.pickup_spritesheet.get_image(192, 0, pick_up_sprites["step_x"], pick_up_sprites["step_y"], 2 * TILESIZE, 2 * TILESIZE)

        # load player animations
        self.load_animations(self.player_animations["idle"], self.player_spritesheet,  0, 0, PLAYER_WIDTH, PLAYER_HEIGHT, 1)
        self.load_animations(self.player_animations["walk"], self.player_spritesheet, 1, 0, PLAYER_WIDTH, PLAYER_HEIGHT, 4)
        self.load_animations(self.player_animations["jump"], self.player_spritesheet, 5, 0, PLAYER_WIDTH, PLAYER_HEIGHT, 1)
        self.load_animations(self.player_animations["fall"], self.player_spritesheet, 1, 1, PLAYER_WIDTH, PLAYER_HEIGHT, 5)
        self.load_animations(self.player_animations["die"], self.player_spritesheet, 0, 3, PLAYER_WIDTH, PLAYER_HEIGHT, 10)
        # load enemy animations
        self.load_animations(self.ctpll_animations["walk"], self.enemy_spritesheet, 0, 1, ENEMY_WIDTH, ENEMY_HEIGHT, 2)
        self.load_animations(self.bird_animations["fly"], self.enemy_spritesheet, 7, 0, ENEMY_WIDTH, ENEMY_HEIGHT, 2)
        self.load_animations(self.spider_animations["walk"], self.enemy_spritesheet, 10, 1, ENEMY_WIDTH, ENEMY_HEIGHT, 2)
        # load missile animations
        self.load_animations(self.missile_animations["fly"], self.enemy_spritesheet, 2, 5, MISSILE_WIDTH, MISSILE_HEIGHT, 1)
        self.load_animations(self.missile_animations["explode"], self.enemy_spritesheet, 2, 5, MISSILE_WIDTH, MISSILE_HEIGHT, 3)

    def load_animations(self, anim_dict, spritesheet, col, row, w_new, h_new, image_count):

        anim_dict["R"] = spritesheet.load_animation(col, row, w_new, h_new, image_count)
        for frame in anim_dict["R"]:
            anim_dict["L"].append(pygame.transform.flip(frame, True, False))

    def animate(self, sprite):

        time_period = sprite.animations[sprite.actionvar]["T"] / len(sprite.animations[sprite.actionvar][sprite.direction])  # time period for which a single anim frame displayed

        rem_new = self.elapsed_time % time_period  # remainder used to detect when elapsed time has increased by a single time period, and therefore go to next frame
        if rem_new < sprite.rem_past:
            sprite.current_frame += 1

        sprite.rem_past = rem_new

        if sprite.current_frame == len(sprite.animations[sprite.actionvar][sprite.direction]):  # if on last frame
            sprite.current_frame = 0  # reset for next animation
            return True

        sprite.image = sprite.animations[sprite.actionvar][sprite.direction][sprite.current_frame]

    def new(self):  # start a new game

        self.score = 0  # players score
        plf_coords = []  # store rect.x, rect.y for each platform tile generated
        self.thread_coords = []  # for drawing spider threads

        # init sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.pick_ups = pygame.sprite.Group()
        self.missiles = pygame.sprite.Group()

        # load map data from map.txt file: create platform, player, enemy sprites accordingly
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):

                if tile == '1':
                    ptf = Platform(col, row, self.pltf_image)
                    self.platforms.add(ptf)
                    self.all_sprites.add(ptf)
                    plf_coords.append((col, row))

                elif tile == 'p':
                    self.player = Player(self, col, row, 1, 2, self.player_animations)
                    self.all_sprites.add(self.player)

                elif tile == 'c':
                    caterpillar = Caterpillar(self, col, row, 1, 1, self.ctpll_animations)
                    self.enemies.add(caterpillar)
                    self.all_sprites.add(caterpillar)

                elif tile == 'b':
                    bird = Bird(self, col, row, 1, 1, self.bird_animations)
                    self.enemies.add(bird)
                    self.all_sprites.add(bird)

                elif tile == 's':
                    spider = Spider(self, col, row, 1, 1, self.spider_animations)
                    self.enemies.add(spider)
                    self.all_sprites.add(spider)

        # generate pickups at random locations along platforms
        random.shuffle(plf_coords)
        for i in range(1, 100):  # 100 pickups
            col = plf_coords[i][0]
            row = plf_coords[i][1] - 1  # move pick_up on top of platform
            image = self.pick_up_images[i % 32]  # cycle through 32 available images for pick ups (reset to first image after 32nd)

            if i % 50 == 0:  # generate speedboost every 50 iterations
                pick_up = Speedboost(plf_coords[i][0], plf_coords[i][1] - 2, self.speedboost_image)
            elif i % 51 == 0:  # generate jumpboost every 51 iterations
                pick_up = Jumpboost(plf_coords[i+1][0], plf_coords[i+1][1] - 2, self.jumpboost_image)
            else:
                pick_up = Pick_up(col, row, image)  # standard pickup which increase points tally

            self.pick_ups.add(pick_up)
            self.all_sprites.add(pick_up)

        self.run()

    def events(self):
        # Game Loop - events

        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_LCTRL:
                    self.player.shoot()

                if event.key == pygame.K_q:
                    self.playing = False

    def update(self):
        # Game Loop - Update
        self.animate(self.player)
        for enemy in self.enemies:
            self.animate(enemy)
        for missile in self.missiles:
            self.animate(missile)

        self.all_sprites.update()
        self.camera.update(self.player)  # change camera rect position so that centred on player rect

    def draw(self):
        # Game Loop - draw
        pygame.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        # self.screen.fill(BLACK)
        self.screen.blit(self.background, (0, 0))  # draw background
        for sprite in self.platforms:  # draw platforms first
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        for sprite in self.pick_ups:
            self.screen.blit(sprite.image, self.camera.apply(sprite))

        self.screen.blit(self.player.image, self.camera.apply(self.player))
        for sprite in self.enemies:
            self.screen.blit(sprite.image, self.camera.apply(sprite)) # draw enemies last

        for sprite in self.missiles:
            self.screen.blit(sprite.image, self.camera.apply(sprite))

        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)
        self.draw_text(str(self.player.actionvar), 22, RED, WIDTH-50, 15)
        self.draw_threads()

        pygame.display.flip()

    def draw_text(self, text, size, colour, x, y):

        font = pygame.font.Font('freesansbold.ttf', size)  # text font
        text_surface = font.render(text, True, colour)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def draw_threads(self):

        for coord_set in self.thread_coords:
            x1 = coord_set[0][0] + self.camera.rect.x
            y1 = coord_set[0][1] + self.camera.rect.y
            x2 = coord_set[1][0] + self.camera.rect.x
            y2 = coord_set[1][1] + self.camera.rect.y

            pygame.draw.line(self.screen, WHITE, (x1, y1), (x2, y2))

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:  # MAIN GAME LOOP
            self.dt = self.clock.tick(FPS) / 1000  # seconds
            self.elapsed_time += self.dt
            self.events()
            self.update()
            self.draw()

    def gameover(self):
        print("GameOver!")
        self.show_gameover()

    def wait_for_key(self):

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    waiting = False

            self.clock.tick(FPS)

    def show_start_screen(self):
        # game splash/start screen
        self.screen.fill(LIGHTGREEN)
        self.draw_text(TITLE, 48, RED, WIDTH/2, HEIGHT/4)
        self.draw_text("Arrows Left/Right, Space to jump", 22, RED, WIDTH/2, HEIGHT/2)
        self.draw_text("Press any key to continue", 22, RED, WIDTH/2, HEIGHT*3/4)
        self.draw_text("High Score: " + str(self.highscore), 22, RED, WIDTH/2, 15)
        pygame.display.flip()
        self.wait_for_key()

    def show_gameover(self):
        if not self.running:
            return
        self.screen.fill(LIGHTGREEN)
        self.draw_text("GAME OVER", 48, RED, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Score:" + str(self.score), 22, RED, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press any key to restart", 22, RED, WIDTH / 2, HEIGHT * 3 / 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HIGH SCORE", 22, RED, WIDTH/2, HEIGHT/2+40)
            with open(path.join(self.dir, HIGHSCORE_FILE), 'w') as f:
                f.write(str(self.score))

        pygame.display.flip()
        self.wait_for_key()


g = Game()
g.show_start_screen()

while g.running:
    g.new()
    g.gameover()

pygame.quit()