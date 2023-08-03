from scripts.entities.entity import Entity

from scripts.tools.spritesheet_loader import load_spritesheet
from scripts.tools import get_sprite_colors

from scripts.visual_fx.particle import Circle

import pygame
import inspect
import random
import sys
import os

def get_all_decoration():
    decoration_list = [t for t in inspect.getmembers(sys.modules[__name__], inspect.isclass)]
			
    return decoration_list

class Decoration(Entity):
    def __init__(self, position, img, dimensions, strata=None, alpha=None):
        super().__init__(position, img, dimensions, strata, alpha)
        self.sprite_id = 'decoration'

    def display(self, scene, dt):
        super().display(scene, dt)

class DecorationBackground(Decoration):
    def __init__(self, position, img, dimensions, strata=None, alpha=None):
        surface = pygame.Surface(img.get_size()).convert_alpha()
        surface.fill((0, 0, 0))
        surface.set_alpha(100)

        img.blit(surface, (0, 0))
        img.set_colorkey((0, 0, 0))

        super().__init__(position, img, dimensions, strata, alpha)
        self.secondary_sprite_id = 'decoration_background'

    def display(self, scene, dt):
        super().display(scene, dt)

class DecorationTorch(Decoration):
    def __init__(self, position, img, dimensions, strata=None, alpha=None):
        super().__init__(position, img, dimensions, strata, alpha)
        self.secondary_sprite_id = 'decoration_torch'

        self.image_frames = load_spritesheet(os.path.join('resources', 'images', 'entities', 'decoration', 'torch-flame.png'), scale=2)
        self.image_offset = [0, 35]

        self.frame = random.randint(0, len(self.image_frames) - 1)
        self.pace = .3

        self.particle_count = [0, 25]
        
    def display(self, scene, dt):
        if self.frame > len(self.image_frames) - 1:
            self.frame = 0
        
        img = self.image_frames[round(self.frame)]
        pos = [self.center_position[0] + self.image_offset[0], self.center_position[1] + self.image_offset[1]]

        glow_img = pygame.transform.scale(img, (img.get_width() * 1.4, img.get_height() * 1.4))
        glow_img.set_alpha(img.get_alpha() * .2)

        scene.entity_surface.blit(glow_img, glow_img.get_rect(center=pos))
        scene.entity_surface.blit(img, img.get_rect(center=pos))

        self.frame += 1 * self.pace * dt
        self.particle_count[0] += 1 * dt

        if self.particle_count[0] >= self.particle_count[1]:
            self.particle_count[0] = 0

            cir = Circle(pos, get_sprite_colors(img)[0], random.randint(3, 5), 0)
            cir.set_goal(90, position=[pos[0] + random.randint(-50, 50), pos[1] + random.randint(-125, -75)], radius=0)
            cir.set_gravity(2)
            cir.glow['active'] = True
            cir.glow['size'] = 2
            cir.glow['intensity'] = .25

            scene.add_sprites(cir)

        super().display(scene, dt)
