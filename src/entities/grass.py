from src.constants import SCREEN_DIMENSIONS

from src.engine import (
    Entity,
    apply_point_rotation,
    get_distance
)

from src.spritesheet_loader import load_standard

from src.entities.player import Player

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

        self.calc_distance = SCREEN_DIMENSIONS[0] / 2

        self.original_position = pygame.Vector2(self.rect.midbottom)
        self.rotation_point = pygame.Vector2(self.image.get_width() / 2, self.image.get_height())

        self.current_rotation = 0
        self.per_rotation = 4
        self.max_rotation = round(self.image.get_height() * 1.75)

    def apply_focus_collision(self, focus, dt):
        if abs(get_distance(self, focus)) > self.calc_distance:
            return

        if self.original_rect.colliderect(focus.rect):
            dist = (focus.rect.x + focus.rect_offset.x) - self.original_position.x
            if dist % 2 != 0:
                dist += 1

            if self.current_rotation < 0:
                if dist > 0:
                    return

            elif self.current_rotation > 0:
                if dist < 0:
                    return

            rotation = -(abs(dist * 2) - self.max_rotation)

            if dist < 0:
                self.current_rotation -= (self.per_rotation * 2) * dt
            
            elif dist > 0:
                self.current_rotation += (self.per_rotation * 2) * dt

            if abs(self.current_rotation) >= rotation:
                if self.current_rotation > 0:
                    self.current_rotation = rotation

                else:
                    self.current_rotation = -rotation

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
            if isinstance(sprite, Player):
                focus = sprite
                break

        self.apply_focus_collision(focus, dt)
        scene.entity_surface.blit(self.image, self.rect)
