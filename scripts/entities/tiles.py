from scripts.prefabs.entity import Entity

from scripts.services import load_spritesheet

import pygame
import inspect
import sys
import os

def get_all_tiles():
    tile_list = [t for t in inspect.getmembers(sys.modules[__name__], inspect.isclass)]
			
    return tile_list

class Tile(Entity):
    def __init__(self, position, img, dimensions, strata=None, alpha=None):
        super().__init__(position, img, dimensions, strata, alpha)
        self.sprite_id = 'tile'

    def display(self, scene, dt):
        super().display(scene, dt)

class Block(Tile):
    def __init__(self, position, img, dimensions, strata=None):
        super().__init__(position, img, dimensions, strata)
        self.secondary_sprite_id = 'block'

    def display(self, scene, dt):
        super().display(scene, dt)

class Ramp(Tile):
    def __init__(self, position, image, direction, strata=None):
        position = list(position)

        super().__init__(position, image, None, strata)
        self.secondary_sprite_id = 'ramp'

        self.direction = direction

        self.width = self.rect.width
        self.height = self.rect.height

    def get_y_value(self, sprite):
        if self.direction == 'left':
            dist = self.rect.left - sprite.rect.right

            if dist >= 0:
                return sprite.rect.bottom
            
            abs_pos = (abs(dist))

            if abs_pos > self.width:
                abs_pos = self.width

            value = round((self.image.get_rect().bottom + self.rect.y) - (self.height * (abs_pos / self.width)))

            return value

        elif self.direction == 'right':
            dist = self.rect.right - sprite.rect.left
            if dist <= 0:
                return sprite.rect.bottom
            
            abs_pos = (abs(dist))

            if abs_pos > self.width:
                abs_pos = self.width

            value = round((self.image.get_rect().bottom + self.rect.y) - (self.height * (abs_pos / self.width)))
            
            return value

    def display(self, scene, dt):
        super().display(scene, dt)

class Platform(Tile):
    def __init__(self, position, img, dimensions, strata=None):
        super().__init__(position, img, dimensions, strata)
        self.secondary_sprite_id = 'platform'

    def display(self, scene, dt):
        super().display(scene, dt)

class Killbrick(Tile):
    def __init__(self, position, img, dimensions, strata=None):
        img.fill((0, 0, 0))

        super().__init__(position, img, dimensions, strata)
        self.secondary_sprite_id = 'killbrick'

    def display(self, scene, dt):
        super().display(scene, dt)