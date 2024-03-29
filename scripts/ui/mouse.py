from scripts.ui.frame import Frame

from scripts.tools import check_pixel_collision

import pygame
import os

class Mouse(pygame.sprite.Sprite):
    def __init__(self):
        self.image = pygame.image.load(os.path.join('resources', 'images', 'ui', 'mouse.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (32, 32))

        self.rect = self.image.get_rect()
        self.entity_pos = [0, 0]

    @property
    def mask(self):
        return pygame.mask.from_surface(self.image)
    
    def check_ui_hover(self, scene):
        for sprite in [s for s in scene.sprite_list if isinstance(s, Frame)]:
            if not check_pixel_collision(self, sprite):
                if not self.rect.colliderect(sprite.hover_rect):
                    if sprite.hovering:
                        sprite.on_hover_end(scene)

                continue
            
            if not sprite.hovering:
                sprite.on_hover_start(scene)

    def display(self, scene, screen):
        self.rect.center = pygame.mouse.get_pos()

        self.entity_pos[0] = self.rect.centerx + scene.camera_offset[0]
        self.entity_pos[1] = self.rect.centery + scene.camera_offset[1]

        self.check_ui_hover(scene)

        screen.blit(self.image, self.rect)
