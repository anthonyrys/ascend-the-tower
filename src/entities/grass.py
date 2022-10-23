from src.constants import SCREEN_DIMENSIONS

from src.engine import (
    apply_point_rotation,
    get_distance
)

from src.spritesheet_loader import load_standard

from src.entities.entity import Entity, Tags

import pygame
import random
import os

class Grass(Entity):
    def __init__(self, position, strata=...):
        imgs = load_standard(os.path.join('imgs', 'grass.png'), os.path.join('data', 'grass.json'))

        img = imgs[random.randint(0, len(imgs) - 1)]
        img = pygame.transform.scale(img, pygame.Vector2(img.get_width() * 2, img.get_height() * 2))
        if random.randint(0, 1) == 1:
            img = pygame.transform.flip(img, True, False)
        img.set_colorkey(pygame.Color(0, 0, 0))
        
        super().__init__(position, img, ..., strata)
        self.rect.midbottom = position
    
        self.original_position = pygame.Vector2(self.rect.midbottom)
        self.rotation_point = pygame.Vector2(self.image.get_width() / 2, self.image.get_height())

        self.current_rotation = 0
        self.per_rotation = 4
        self.max_rotation = 40

    def apply_rotation(self, focus, dt):
        if abs(get_distance(self, focus)) > SCREEN_DIMENSIONS[1] / 2:
            return

        if self.original_rect.colliderect(focus.rect):
            dist = (focus.rect.x + focus.rect_offset.x) - self.original_position.x
            if dist % 2 != 0:
                dist += 1

            self.max_rotation = abs(dist * 2)

            if dist < 0:
                self.current_rotation -= (self.per_rotation * 2) * dt
            
            if dist > 0:
                self.current_rotation += (self.per_rotation * 2) * dt

            if abs(self.current_rotation) >= self.max_rotation:
                if self.current_rotation > 0:
                    self.current_rotation = self.max_rotation

                else:
                    self.current_rotation = -self.max_rotation

        else:
            if self.current_rotation > 0:
                self.current_rotation -= self.per_rotation * dt

            elif self.current_rotation < 0:
                self.current_rotation += self.per_rotation * dt

            if abs(self.current_rotation) <= self.per_rotation:
                self.current_rotation = 0

        apply_point_rotation(self, self.original_position, self.rotation_point, self.current_rotation)

    def display(self, scene, dt):
        focus = None
        for sprite in scene.sprites:
            if sprite.get_tag(Tags.PLAYER):
                focus = sprite
                break

        self.apply_rotation(focus, dt)
        scene.entity_surface.blit(self.image, self.rect)
