from src.constants import (
    COLOR_VALUES
)

from src.engine import Entity
from src.particle_fx import Outline

import pygame

class Barrier(Entity):
    def __init__(self, position, dimensions, color, player):
        super().__init__(position, pygame.Color((COLOR_VALUES[color])), dimensions, 2) 
        
        self.image.convert_alpha()
        self.player = player

        self.color = color
        self.color_alpha = 128
        self.prev_state = None

    def set_color(self, scene):
        self.image.fill(COLOR_VALUES[self.color])

        if self.color == self.player.color:
            if self.prev_state:
                particles = Outline(
                    Outline.Info(pygame.Vector2(self.image.get_width() * 1.5, self.image.get_height() * 1.5), 30, 1),
                    pygame.Vector2(self.rect.center), COLOR_VALUES[self.color], 3, self.image.copy(), self.strata + 1
                )
                
                scene.add_sprites(particles)

            if self.image.get_alpha() == self.color_alpha:
                self.image.set_alpha(255)

            self.prev_state = False

        else:
            if not self.prev_state:
                ...

            self.image.set_alpha(self.color_alpha)

            self.prev_state = True

    def display(self, scene, dt):
        self.set_color(scene)
        scene.entity_surface.blit(self.image, self.rect)
