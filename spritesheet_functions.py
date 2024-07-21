"""
This module is used to pull individual sprites from sprite sheets.
"""
import pygame
from os import path

class SpriteSheet():
    """ Class used to grab images out of a sprite sheet and return to animation list """

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 255)

    def __init__(self, spritesheet_dict):
        """ Constructor. Pass in the file name of the sprite sheet. """
        self.spritesheet_dict = spritesheet_dict  # load sprite sheet dictionary from settings
        self.sprite_sheet = pygame.image.load(path.join("Images", spritesheet_dict["file_name"])).convert()  # Load the sprite sheet image file
        self.backgroundcolour = spritesheet_dict["background"]

    def get_image(self, x, y, width, height, w_new, h_new):
        """ Grab a single image out of a larger spritesheet
            Pass in the x, y location of the sprite
            and the width and height of the sprite. """
        image = pygame.Surface([width, height]).convert()  # Create a new blank image
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))  # Copy the sprite from the large sheet onto the smaller image
        image = pygame.transform.scale(image, (w_new, h_new))  # resize image
        # Assuming black works as the transparent color
        image.set_colorkey(self.backgroundcolour)
        return image

    def load_animation(self, col, row, w_new, h_new, image_count):
        """ Resize individual image to w_new by h_new according to sprite dimensions and append to animation list."""

        animation = []
        i = col * self.spritesheet_dict["step_x"]  # pixel coords of first sprite top left hand corner
        j = row * self.spritesheet_dict["step_y"]

        col = 0
        while len(animation) < image_count:

            if col < self.spritesheet_dict["image_per_row"]:
                image = self.get_image(i, j, self.spritesheet_dict["step_x"], self.spritesheet_dict["step_y"], w_new, h_new)
                animation.append(image)
                i += self.spritesheet_dict["step_x"]
                col += 1
            else:
                i = 0
                col = 0
                j += self.spritesheet_dict["step_y"]

        return animation

