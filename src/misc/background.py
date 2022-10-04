from src.constants import (
    SCREEN_DIMENSIONS,
    BG_COLOR
)

import pygame
import os

class Background():
    def __init__(self):
        self.imgs = dict()
        self.img_speed = 1

        img = self.create_img()

        self.imgs[img.copy()] = pygame.Vector2(pygame.Vector2(-720, 0))
        self.imgs[img.copy()] = pygame.Vector2()
        self.imgs[img.copy()] = pygame.Vector2(pygame.Vector2(720, 0))

    def create_img(self):
        img_path = os.path.join('imgs', 'misc', 'background.png')
        img = pygame.image.load(img_path).convert_alpha()

        img = pygame.mask.from_surface(img).to_surface(
            setcolor=BG_COLOR, 
            unsetcolor=pygame.Color(0, 0, 0, 0)
        )

        img = pygame.transform.scale(img, pygame.Vector2(720, 720))

        return img

    def display(self, display_surface):
        for img, pos in self.imgs.items():
            if pos.x == SCREEN_DIMENSIONS[0]:
                pos.x = -880

            pos.x += self.img_speed
            
            display_surface.blit(img, pos)
