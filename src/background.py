from src.constants import (
    SCREEN_DIMENSIONS,
    BG_COLOR
)

import pygame
import os

class Background():
    def __init__(self):
        img_path = os.path.join('imgs', 'background.png')

        img = pygame.image.load(img_path).convert_alpha()
        img = pygame.transform.scale(img, pygame.Vector2(SCREEN_DIMENSIONS[1] * 2, SCREEN_DIMENSIONS[1]))
        img = pygame.mask.from_surface(img).to_surface(
            setcolor=BG_COLOR,
            unsetcolor=pygame.Color(0, 0, 0, 0)
        )

        self.imgs = {
            img.copy(): pygame.Vector2(-img.get_width(), 0),
            img.copy(): pygame.Vector2()
        }

        self.scroll_speed = .75

    def display(self, display_surface, dt):
        for img, pos in self.imgs.items():
            if pos.x >= SCREEN_DIMENSIONS[0]:
                pos.x = -img.get_width()

            display_surface.blit(img, pos)
            pos.x += self.scroll_speed * dt
