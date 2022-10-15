from src.constants import (
    GRAVITY,
    MAX_GRAVITY
)

from src.entities.interactable import Interactable
from src.entities.entity import Tags

import pygame

class Rock(Interactable):
    def __init__(self, position, img, dimensions, strata):
        super().__init__(position, img, dimensions, strata)
        
        self.base_strata = strata
        self.offset = pygame.Vector2(0, 8)

    def apply_gravity(self, dt):
        if not self.collide_points['bottom']:
            self.velocity.y += GRAVITY * dt if self.velocity.y < MAX_GRAVITY * dt else 0

        else:
            self.velocity.y = GRAVITY * dt

    def apply_collision_x(self, scene):
        self.collide_points['right'] = False
        self.collide_points['left'] = False

        collidables = [s for s in scene.sprites if s.get_tag(Tags.COLLIDABLE)]
        for collidable in collidables:
            if not self.rect.colliderect(collidable.rect):
                continue

            if collidable.rect.collidepoint(self.rect.midleft):
                self.rect.left = collidable.rect.right
                self.collide_points['left'] = True

            if collidable.rect.collidepoint(self.rect.midright):
                self.rect.right = collidable.rect.left
                self.collide_points['right'] = True

    def apply_collision_y(self, scene):
        self.collide_points['top'] = False
        self.collide_points['bottom'] = False

        collidables = [s for s in scene.sprites if s.get_tag(Tags.COLLIDABLE)]
        for collidable in collidables:
            if not self.rect.colliderect(collidable.rect):
                continue

            if self.rect.bottom > collidable.rect.top:
                self.rect.bottom = collidable.rect.top

                self.collide_points['bottom'] = True
                self.velocity.y = 0

            elif self.rect.top < collidable.rect.bottom:
                self.rect.top = collidable.rect.bottom

                self.collide_points['top'] = True
                self.velocity.y = 0

    def on_interact(self, interacter):
        self.interacter = interacter
        self.interacting = True

        self.strata = interacter.strata + 1

        return 0

    def on_release(self):
        self.interacter = None
        self.interacting = False
        self.strata = self.base_strata
    
    def display(self, scene, dt):
        if not self.interacting:
            self.apply_gravity(dt)

            self.rect.x += self.velocity.x * dt
            self.apply_collision_x(scene)

            self.rect.y += self.velocity.y * dt
            self.apply_collision_y(scene)

        else:
            direction = self.interacter.rect.left if self.interacter.direction < 0 else self.interacter.rect.right
            center = self.interacter.mask.centroid()[1]

            self.rect.center = pygame.Vector2(
                direction, 
                self.interacter.rect.centery + (center - self.image.get_height())
            ) + self.offset

        scene.entity_surface.blit(self.image, self.rect)
