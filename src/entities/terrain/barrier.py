from src.constants import (
    COLORS,
    COLOR_VALUES,
    COLOR_VALUES_SECONDARY,
)
from src.entities.entity import Entity, Tags
from src.entities.particle import Outline

import pygame

class ColorBarrier(Entity):
    def __init__(self, position, dimensions, color, player):
        super().__init__(position, pygame.Color((COLOR_VALUES[color])), dimensions, 3) 
        self.add_tags(Tags.BARRIER)
        
        self.image.convert_alpha()
        self.player = player

        self.color = color
        self.color_alpha = 128
        self.prev_state = None

    def set_color(self, scene):
        self.image.fill(COLOR_VALUES[self.color])

        if self.color == self.player.color:
            if self.prev_state:
                pos = pygame.Vector2(self.rect.centerx, self.rect.centery)
                particles = Outline(
                    Outline.Info(pygame.Vector2(self.image.get_width() * 1.5, self.image.get_height() * 1.5), 30, 1),
                    pos, COLOR_VALUES[self.color], 3, self.image.copy(), self.strata + 1
                )
                
                scene.add_sprites(particles)

            if self.image.get_alpha() == self.color_alpha:
                self.image.set_alpha(255)

            self.prev_state = False

        else:
            if not self.prev_state:
                pos = pygame.Vector2(self.rect.centerx, self.rect.centery)
                particles = Outline(
                    Outline.Info(pygame.Vector2(self.image.get_width() * 1.5, self.image.get_height() * 1.5), 30, 1),
                    pos, COLOR_VALUES[self.color], 3, self.image.copy(), self.strata + 1
                )
                
                scene.add_sprites(particles)

            self.image.set_alpha(self.color_alpha)

            self.prev_state = True

    def display(self, scene, dt):
        self.set_color(scene)
        scene.sprite_surface.blit(self.image, self.rect)
