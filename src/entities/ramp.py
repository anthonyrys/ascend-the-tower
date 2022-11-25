from src.engine import Entity
from src.spritesheet_loader import load_standard

import pygame
import os

class Ramp(Entity):
    def __init__(self, position, ramp_type, direction, strata=None):
        imgs = load_standard(os.path.join('imgs', 'ramps.png'), 'ramps')
        img = imgs[ramp_type]

        position = list(position)

        if ramp_type == 1:
            img_size = img.get_size()

            surf = pygame.Surface((img_size[0], img_size[1] / 2)).convert_alpha()
            surf.blit(img, (0, -img_size[1] / 2))
            surf.set_colorkey((0, 0, 0))

            img = surf
            position[1] += img.get_height() * 6
            
        img_size = img.get_size()
        img = pygame.transform.scale(img, (img_size[0] * 6, img_size[1] * 6)).convert_alpha()

        if direction == 'left':
            img = pygame.transform.flip(img, True, False).convert_alpha()

        super().__init__(position, img, None, strata)

        self.ramp_type = ramp_type
        self.direction = direction

        self.width = self.rect.width
        self.height = self.rect.height

    def get_y_value(self, sprite):
        if self.direction == 'right':
            dist = self.rect.left - sprite.rect.right

            if dist >= 0:
                return sprite.rect.bottom
            
            abs_pos = (abs(dist))

            if abs_pos > self.width:
                abs_pos = self.width

            return round((self.image.get_rect().bottom + self.rect.y) - (self.height * (abs_pos / self.width)))

        elif self.direction == 'left':
            dist = self.rect.right - sprite.rect.left
            if dist <= 0:
                return sprite.rect.bottom
            
            abs_pos = (abs(dist))

            if abs_pos > self.width:
                abs_pos = self.width

            return round((self.image.get_rect().bottom + self.rect.y) - (self.height * (abs_pos / self.width)))

    def display(self, scene, dt):
        super().display(scene, dt)
        