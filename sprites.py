import pygame
from math import fabs
from math import sqrt as sqrt
from settings import *
from spritesheet_functions import *
vec = pygame.math.Vector2  # 2D vector - x = vec.x  y = vec.y

class Static_sprite(pygame.sprite.Sprite):

    def __init__(self, start_x, start_y, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()
        self.pos = vec(start_x * TILESIZE, start_y * TILESIZE)  # position in pixels
        self.rect.topleft = self.pos

class Mobile_sprite(pygame.sprite.Sprite):

    def __init__(self, game, start_x, start_y, width, height, animations):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pygame.Surface((width*TILESIZE, height*TILESIZE))
        self.rect = self.image.get_rect()
        self.pos = vec(start_x * TILESIZE, start_y * TILESIZE)  # position in pixels
        self.vel = vec(0, 0)  # velocity vector
        self.rect.topleft = self.pos

        self.animations = animations  # assign corresponding animations dict to sprite
        self.current_frame = 0
        self.time_at = 0  # recording elapsed game time e.g. on keydown event (to limit time player can jump for example)
        self.rem_past = 0  # remainder used to detect when elapsed time has increased by a single time period, and therefore go to next animation frame
        self.direction = "R"  # player facing left or right

        self.actionvar = "fall"  # current player action
        self.newaction = "fall"  # new player action on keyboard input- jumping, walking etc

    def collide_platforms(self, platforms):

        self.rect.y += 1  # move player rect down a pixel to check for collision with platform
        hits = pygame.sprite.spritecollide(self, platforms, False)
        self.rect.y -= 1  # move back up having check for collision
        if len(hits) > 0 and self.vel.y >= 0:  # can only fall onto platforms- able to jump through them

            if self.pos.y < hits[0].rect.bottom:  # bottom of sprite rect above bottom of platform rect
                self.pos.y = hits[0].rect.top  # set sprite y position to top of platform
                return True

    def change_action(self, newaction):
        """ change action from e.g. jumping to falling.  First check current action to see if action has actually changed then return new actionvar"""
        if self.actionvar != newaction:
            if self.actionvar != "die":
                self.actionvar = newaction
                self.current_frame = 0


class Player(Mobile_sprite):

    def __init__(self, game, start_x, start_y, width, height, animations):
        super().__init__(game, start_x, start_y, width, height, animations)

        self.runspeed = 4
        self.jumpspeed = 12
        self.jumptime = 0.4
        self.newaction = "fall"
        self.dead = False

    def collide_enemy(self, enemies):

        # collision with enemy from all other directions (players death)
        hits = pygame.sprite.spritecollide(self, enemies, False, pygame.sprite.collide_rect_ratio(0.7))  # check hits to the right

        if hits and self.vel.y > 0:
            hits[0].kill()

        elif hits:
            self.dead = True
            self.newaction = "die"

    def collide_pick_up(self, pick_ups):

        hits = pygame.sprite.spritecollide(self, pick_ups, False, pygame.sprite.collide_rect_ratio(0.5))
        if hits:
            hits[0].kill()
            hits[0].apply_pickup(self)

    def jump(self):

        if self.vel.y == 0:  # on platform
            self.vel.y = -self.jumpspeed
            self.newaction = "jump"
            self.time_at = self.game.elapsed_time
        elif self.game.elapsed_time - self.time_at < self.jumptime:  # already jumping
            self.vel.y = -self.jumpspeed
            self.newaction = "jump"

    def shoot(self):

        self.missile = Missile(self.game, self.rect.centerx, self.rect.centery, 1, 1, self.game.missile_animations, self)
        self.game.missiles.add(self.missile)
        self.game.all_sprites.add(self.missile)

    def update(self):

        # self.vel = vec(0, FALL_VELOCITY)

        keys = pygame.key.get_pressed()

        # Check platform collision
        if self.collide_platforms(self.game.platforms) is True:
            self.vel = vec(0, 0)
            self.newaction = "idle"
        else:
            self.vel = vec(0, FALL_VELOCITY)
            self.newaction = "fall"

        # KEY INPUT
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel.x = -self.runspeed
            self.direction = "L"

        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel.x = self.runspeed
            self.direction = "R"

        if keys[pygame.K_SPACE] or keys[pygame.K_j]:
            self.jump()  # change self.newaction to "jump", if applicable

        if self.vel.y == 0 and self.vel.x != 0:
            self.newaction = "walk"

        # check sprite collisions
        self.collide_enemy(self.game.enemies)
        self.collide_pick_up(self.game.pick_ups)

        self.change_action(self.newaction)  # change self.actionvar to new action

        if self.dead:
            self.vel = vec(0, 10)
            if self.current_frame + 1 == len(self.game.player_animations["die"][self.direction]):  # on last frame of death animation
                self.game.playing = False

        # wrap around the sides of the screen
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.pos += self.vel
        self.rect.midbottom = self.pos


class Missile(Mobile_sprite):

    def __init__(self, game, start_x, start_y, width, height, animations, player):

        self.image = pygame.Surface((MISSILE_WIDTH, MISSILE_HEIGHT))
        super().__init__(game, start_x, start_y, width, height, animations)
        self.pos = vec(player.rect.centerx, player.rect.centery)  # position and vel need reassignment for missile class
        self.vel = vec(10, 0)
        if player.direction == "L":
            self.vel.x *= -1  # reverse bullet direction
            self.direction = "L"

        self.actionvar = "fly"
        self.newaction = "fly"
        self.animations = animations  # assign corresponding animations dict to sprite

    def collide_enemy(self, enemies):

        hits = pygame.sprite.spritecollide(self, enemies, False, pygame.sprite.collide_rect_ratio(0.7))
        if hits:
            hits[0].kill()
            self.newaction = "explode"

    def update(self):

        self.pos += self.vel
        self.collide_enemy(self.game.enemies)
        self.rect.center = self.pos
        self.change_action(self.newaction)

        if self.actionvar == "explode":
            self.vel = (0, 0)
            if self.current_frame + 1 == len(self.game.missile_animations["explode"][self.direction]):  # on last frame of explosion animation
                self.kill()

        if self.pos.x < 0 or self.pos.x > WIDTH:
            self.kill()  # if bullet goes off screen


class Caterpillar(Mobile_sprite):

    def __init__(self, game, start_x, start_y, width, height, animations):
        super().__init__(game, start_x, start_y, width, height, animations)

        self.vel = vec(CTPLL_SPEED, 0)

        self.actionvar = "walk"  # only walk back and forth along platforms
        self.animations = animations  # assign corresponding animations dict to sprite

    def turn_around(self):

        d = self.vel.x / fabs(self.vel.x)  # returns either +/-1 (direction of travel)

        self.rect.x += self.rect.width * d  # check if at platform edge
        if self.collide_platforms(self.game.platforms) is not True:
            self.vel.x *= -1  # turn around
        self.rect.x += self.rect.width*d*-1  # undo rect.x increase

        if self.vel.x > 0:
            self.direction = "R"
        else:
            self.direction = "L"

    def update(self):

        self.turn_around()
        self.pos += self.vel
        self.rect.midbottom = self.pos


class Bird(Mobile_sprite):

    def __init__(self, game, start_x, start_y, width, height, animations):

        super().__init__(game, start_x, start_y, width, height, animations)
        self.actionvar = "fly"
        self.animations = animations  # assign corresponding animations dict to sprite
        self.n_past = 0  # for chase player method

    def chase_player(self, player):

        n = self.game.elapsed_time % 0.5

        if n < self.n_past:  # recalculate disp vector every 1 second

            target_vec = player.pos - self.pos  # displacement vector between player and enemy
            unit_vec = 1 / sqrt(target_vec.x**2 + target_vec.y**2)  # unit vector for displacement

            self.vel.x = target_vec.x * unit_vec * BIRD_SPEED  # resultant x velocity
            self.vel.y = target_vec.y * unit_vec * BIRD_SPEED

        self.n_past = n

    def update(self):

        if fabs(self.game.player.pos.y - self.pos.y) < HEIGHT:  # if enemy within screen height of player
            self.chase_player(self.game.player)
        else:  # stop chasing player if outside screen height
            self.vel = vec(0, 0)

        self.pos += self.vel
        self.rect.midbottom = self.pos


class Spider(Mobile_sprite):

    def __init__(self, game, start_x, start_y, width, height, animations):
        super().__init__(game, start_x, start_y, width, height, animations)

        self.actionvar = "walk"  # permanenantly set to "walk" as only animation for spider
        self.newaction = "walk"
        self.animations = animations  # assign corresponding animations dict to sprite

    def chase_player(self, player):
        self.newaction = "walk"
        if fabs(player.pos.y - self.pos.y) < HEIGHT*1.5:  # if enemy within 1&half x screen height of player
            target_x = player.pos.x - self.pos.x  # x displacement between player and enemy
            if target_x != 0:
                d = target_x / fabs(target_x)  # returns either +/-1 (direction of travel)
                self.vel.x = SPIDER_SPEED * d  # pursue player along platform

    def climb(self, player):
        """ Climb to platform above when directly underneath player"""
        if fabs(player.pos.y - self.pos.y) < HEIGHT*1.5:  # if enemy within 1&half x screen height of player
            target_x = self.pos.x - player.pos.x  # x displacement between player and enemy
            target_y = self.pos.y - player.pos.y

            if player.actionvar == "idle" or player.actionvar == "walk":
                if target_y > 0 and target_x == 0:  # player on platform directly above

                    self.newaction = "climb"
                    thread_coords = (self.pos[:], player.pos[:])  # start, end position vectors for drawing thread
                    self.game.thread_coords.append(thread_coords)

    def update(self):

        self.vel = vec(0, FALL_VELOCITY)

        if self.collide_platforms(self.game.platforms) is True:
            self.chase_player(self.game.player)
            self.climb(self.game.player)  # change self.newaction = "climb", if aligned with player

        if self.newaction == "climb":
            self.vel.y = -SPIDER_SPEED

        self.pos += self.vel
        self.rect.midbottom = self.pos


class Platform(Static_sprite):

    def __init__(self, start_x, start_y, image):
        "Generates a single platform tile."
        super().__init__(start_x, start_y, image)


class Pick_up(Static_sprite):

    def __init__(self, start_x, start_y, image):
        "Generates a single pick_up tile."
        super().__init__(start_x, start_y, image)

    def apply_pickup(self, player):
        player.game.score += 50


class Speedboost(Pick_up):

    def __init__(self, start_x, start_y, image):
        super().__init__(start_x, start_y, image)

    def apply_pickup(self, player):
        player.runspeed *= 1.5


class Jumpboost(Pick_up):

    def __init__(self, start_x, start_y, image):
        super().__init__(start_x, start_y, image)

    def apply_pickup(self, player):
        player.jumptime *= 1.2
        # player.jumpheight *= 1.5
