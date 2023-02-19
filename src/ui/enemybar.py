from src.engine import Component

import pygame
import os

class Enemybar(Component):
    def __init__(self, sprite):
        img = pygame.image.load(os.path.join('imgs', 'ui', 'enemy-frame.png')).convert_alpha()
        img = pygame.transform.scale(img, (img.get_width() * 1.25, img.get_height() * 1.25))

        super().__init__((0, 0), pygame.Surface((img.get_width(), img.get_height())).convert_alpha(), None, 2)
        self.uses_entity_surface = True
        self.image.set_colorkey((0, 0, 0))

        self.enemy = sprite

        self.content_size = [img.get_width(), img.get_height()]

        self.backdrop = pygame.Surface((self.content_size[0], self.content_size[1])).convert_alpha()
        self.backdrop.fill((24, 24, 26))
        self.original_backdrop = self.backdrop.copy()

        self.health = pygame.Surface((self.content_size[0], self.content_size[1])).convert_alpha()
        self.health.fill((225, 105, 116))
        self.original_health = self.health.copy()

        self.frame = img

    def display(self, scene, dt):
        self.image.fill((0, 0, 0, 0))

        health_percentage = self.enemy.combat_info['health'] / self.enemy.combat_info['max_health']
        self.health = pygame.transform.scale(self.original_health, (self.original_health.get_width() * health_percentage, self.original_health.get_height()))

        self.image.blit(self.backdrop, (0, 0))
        self.image.blit(self.health, (0, 0))
        self.image.blit(self.frame, (0, 0))

        self.rect.x = self.enemy.rect.centerx - self.image.get_width() * .5
        self.rect.y = self.enemy.rect.centery - self.image.get_height() * 3

        super().display(scene, dt)




    
