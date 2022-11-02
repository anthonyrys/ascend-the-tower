from src.constants import SCREEN_DIMENSIONS

from src.engine import (
    Entity,
    get_distance
)

from src.spritesheet_loader import load_standard

import pygame
import random
import os
import math

class Grass(Entity):
    def __init__(self, position, strata=None, focus=None):
        imgs = load_standard(os.path.join('imgs', 'grass.png'), 'grass')

        img = imgs[random.randint(0, len(imgs) - 1)]
        img = pygame.transform.scale(img, pygame.Vector2(img.get_width() * 2, img.get_height() * 2))
        if random.randint(0, 1) == 1:
            img = pygame.transform.flip(img, True, False)
        img.set_colorkey(pygame.Color(0, 0, 0))
        
        super().__init__(position, img, None, strata)
        self.rect.midbottom = position

        self.focus = focus

        self.calc_distance = SCREEN_DIMENSIONS[0] / 2

        self.original_position = pygame.Vector2(self.rect.midbottom)
        self.rotation_point = pygame.Vector2(self.rect.width / 2, self.rect.height)

        self.current_rotation = 0

        self.focus_rotation = 0
        self.per_focus_rotation = 6
        self.max_focus_rotation = round(self.rect.height * 2.2)
        self.rotation_focus_ratio = 1

        self.sin_frequency = .01 + round((self.rect.height * 0.0005 * random.randint(1, 2)), 2)
        self.sin_amplifier = random.randint(1, 4)
        self.frame_rand = random.randint(-5, 5)

    def apply_focus_rotation(self, dt):
        if not self.focus:
            return
            
        if abs(get_distance(self, self.focus)) > self.calc_distance:
            return

        if self.original_rect.colliderect(self.focus.rect):
            dist = (self.focus.rect.x + self.focus.rect_offset.x) - self.original_position.x
            if dist % 2 != 0:
                dist += 1

            if self.focus_rotation < 0:
                if dist > 0:
                    return

            elif self.focus_rotation > 0:
                if dist < 0:
                    return

            rotation = -(abs(dist * 2) - self.max_focus_rotation)

            if dist < 0:
                self.focus_rotation -= (self.per_focus_rotation * 2) * dt
            
            elif dist > 0:
                self.focus_rotation += (self.per_focus_rotation * 2) * dt

            if abs(self.focus_rotation) >= rotation:
                if self.focus_rotation > 0:
                    self.focus_rotation = rotation

                else:
                    self.focus_rotation = -rotation

        else:
            if self.focus_rotation > 0:
                self.focus_rotation -= self.per_focus_rotation * dt

            elif self.focus_rotation < 0:
                self.focus_rotation += self.per_focus_rotation * dt

            if abs(self.focus_rotation) <= self.per_focus_rotation:
                self.focus_rotation = 0

        self.rotation_focus_ratio = round(abs(self.focus_rotation / self.max_focus_rotation), 1)
        if self.rotation_focus_ratio > 1:
            self.rotation_focus_ratio = 1

        if self.rotation_focus_ratio - .1 > 0:
            self.rotation_focus_ratio -= .1

    def apply_passive_rotation(self, dt, frames):
        sin_val = round(self.sin_amplifier * math.sin(self.sin_frequency * (frames + self.frame_rand))) * dt
        if sin_val < 0:
            sin_val += self.rotation_focus_ratio
        if sin_val > 0:
            sin_val -= self.rotation_focus_ratio

        self.current_rotation = self.focus_rotation + sin_val

    def display(self, scene, dt):
        self.apply_focus_rotation(dt)
        self.apply_passive_rotation(dt, scene.frames)

        rect = self.image.get_rect(center = (self.original_position.x - self.rotation_point.x, self.original_position.y - self.rotation_point.y))
        offset = (self.original_position - rect.center).rotate(-self.current_rotation)

        self.image = pygame.transform.rotate(self.original_image, self.current_rotation).convert_alpha()
        self.rect = self.image.get_rect(midtop = ((self.original_position.x - offset.x), self.original_position.y - offset.y))

        scene.entity_surface.blit(self.image, self.rect)
