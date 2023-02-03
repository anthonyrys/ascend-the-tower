from src.constants import PRIMARY_COLOR

import pygame
import os

class Mouse(pygame.sprite.Sprite):
    def __init__(self):
        self.image = pygame.image.load(os.path.join('imgs', 'mouse.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.image = self.mask.to_surface(
            setcolor=PRIMARY_COLOR, 
            unsetcolor=(0, 0, 0, 0)
        )

        self.rect = self.image.get_rect()

    @property
    def mask(self):
        return pygame.mask.from_surface(self.image)

    def display(self, scene):
        self.rect.center = pygame.mouse.get_pos()
        scene.ui_surface.blit(self.image, self.rect)
