from scripts.constants import UI_EXP_COLOR
from scripts.engine import Frame

import pygame
import os

class Expbar(Frame):
    def __init__(self, player):
        img_scale = 3
        img = pygame.image.load(os.path.join('imgs', 'ui', 'player', 'exp-frame.png')).convert_alpha()
        img = pygame.transform.scale(img, (img.get_width() * img_scale, img.get_height() * img_scale))

        super().__init__((0, 0), pygame.Surface((img.get_width(), img.get_height())).convert_alpha(), None, 1)
        self.image.set_colorkey((0, 0, 0)) 

        self.player = player
        self.frame = img
        self.content_size = [img.get_width(), img.get_height()]

        self.backdrop = pygame.Surface((self.content_size[0], self.content_size[1])).convert_alpha()
        self.backdrop.fill((24, 24, 24))

        self.exp = pygame.Surface((self.content_size[0], self.content_size[1])).convert_alpha()
        self.exp.fill(UI_EXP_COLOR)
        self.original_exp = self.exp.copy()

    def display(self, scene, dt):
        percentage = self.player.level_info['experience'] / self.player.level_info['max_experience']
        self.exp = pygame.transform.scale(self.original_exp, (self.original_exp.get_width() * percentage, self.original_exp.get_height()))

        self.image.fill((0, 0, 0, 0))
        self.image.blit(self.backdrop, (0, 0))
        self.image.blit(self.exp, (0, 0))
        self.image.blit(self.frame, (0, 0))

        super().display(scene, dt)



    
