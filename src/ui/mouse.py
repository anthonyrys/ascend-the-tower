import pygame
import os

class Mouse(pygame.sprite.Sprite):
    def __init__(self):
        self.image = pygame.image.load(os.path.join('imgs', 'ui', 'mouse.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (32, 32))

        self.rect = self.image.get_rect()
        self.entity_pos = [0, 0]

    @property
    def mask(self):
        return pygame.mask.from_surface(self.image)

    def display(self, scene):
        self.rect.center = pygame.mouse.get_pos()

        self.entity_pos[0] = self.rect.centerx + scene.camera_offset[0]
        self.entity_pos[1] = self.rect.centery + scene.camera_offset[1]

        scene.ui_surface.blit(self.image, self.rect)
