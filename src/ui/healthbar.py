from src.engine import Frame

import pygame
import os

class Healthbar(Frame):
    def __init__(self, player):
        img = pygame.image.load(os.path.join('imgs', 'ui', 'health-frame.png')).convert_alpha()
        img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))

        super().__init__((0, 0), pygame.Surface((img.get_width(), img.get_height())).convert_alpha(), None, 2)
        self.image.set_colorkey((0, 0, 0))

        self.player = player

        self.content_size = [500, 100]

        self.backdrop = pygame.Surface((self.content_size[0], self.content_size[1])).convert_alpha()
        self.backdrop.fill((24, 24, 26))
        self.original_backdrop = self.backdrop.copy()

        self.health = pygame.Surface((self.content_size[0], self.content_size[1])).convert_alpha()
        self.health.fill((225, 105, 116))
        self.original_health = self.health.copy()

        self.frame = img

    def display(self, scene, dt):
        self.image.fill((0, 0, 0, 0))

        health_percentage = self.player.combat_info['health'] / self.player.combat_info['max_health']
        self.health = pygame.transform.scale(self.original_health, (self.original_health.get_width() * health_percentage, self.original_health.get_height()))

        self.image.blit(self.backdrop, (0, 0))
        self.image.blit(self.health, (0, 0))
        self.image.blit(self.frame, (0, 0))

        super().display(scene, dt)




    
