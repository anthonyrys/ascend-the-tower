from src.constants import UI_HEALTH_COLOR
from src.engine import Frame

import pygame
import os

class Enemybar(Frame):
    def __init__(self, sprite):
        img_scale = 1.25
        img = pygame.image.load(os.path.join('imgs', 'ui', 'hud', 'enemy-frame.png')).convert_alpha()
        img = pygame.transform.scale(img, (img.get_width() * img_scale, img.get_height() * img_scale))

        super().__init__((0, 0), pygame.Surface((img.get_width(), img.get_height())).convert_alpha(), None, 2)
        self.uses_entity_surface = True
        self.image.set_colorkey((0, 0, 0))

        self.enemy = sprite
        self.frame = img

        self.content_size = [img.get_width(), img.get_height()]
        
        self.pulse_info = {
            'surface': pygame.Surface((self.content_size[0], self.content_size[1])).convert_alpha(),
            'original_surface': pygame.Surface((self.content_size[0], self.content_size[1])).convert_alpha(),
            'frames': 0,
            'frames_max': 0 
        }

        self.backdrop = pygame.Surface((self.content_size[0], self.content_size[1])).convert_alpha()
        self.backdrop.fill((24, 24, 24))

        self.health = pygame.Surface((self.content_size[0], self.content_size[1])).convert_alpha()
        self.health.fill(UI_HEALTH_COLOR)
        self.original_health = self.health.copy()

    def set_pulse(self, frames, color):
        self.pulse_info['surface'] = self.pulse_info['original_surface'].copy()
        self.pulse_info['surface'].fill(color)

        self.pulse_info['frames'] = frames
        self.pulse_info['frames_max'] = frames

    def display(self, scene, dt):
        self.image.fill((0, 0, 0, 0))

        health_percentage = self.enemy.combat_info['health'] / self.enemy.combat_info['max_health']
        self.health = pygame.transform.scale(self.original_health, (self.original_health.get_width() * health_percentage, self.original_health.get_height()))

        self.image.blit(self.backdrop, (0, 0))
        self.image.blit(self.health, (0, 0))

        if self.pulse_info['frames'] > 0:
            self.pulse_info['surface'].set_alpha((self.pulse_info['frames'] / self.pulse_info['frames_max']) * 255)
            self.pulse_info['surface'] = pygame.transform.scale(
                self.pulse_info['surface'], 
                (self.pulse_info['original_surface'].get_width() * health_percentage, self.pulse_info['original_surface'].get_height())
            )

            self.image.blit(self.pulse_info['surface'], (0, 0))
            self.pulse_info['frames'] -= 1 * dt

        self.image.blit(self.frame, (0, 0))

        self.rect.x = self.enemy.rect.centerx - self.image.get_width() * .5
        self.rect.y = self.enemy.rect.centery - self.image.get_height() * 3

        super().display(scene, dt)




    
