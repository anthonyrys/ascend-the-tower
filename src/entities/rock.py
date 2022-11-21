from src.constants import (
    GRAVITY,
    MAX_GRAVITY,
    COLOR_VALUES_SECONDARY
)

from src.engine import (
    get_distance,
    create_outline
)

from src.spritesheet_loader import load_standard

from src.entities.interactable import Interactable
from src.entities.tile import Tile
from src.entities.platform import Platform
from src.entities.ramp import Ramp

import pygame
import random
import os

class Rock(Interactable):
    def __init__(self, position, dimensions, strata):
        imgs = load_standard(os.path.join('imgs', 'rocks.png'), 'rocks')

        img = imgs[random.randint(0, len(imgs) - 1)]
        img = pygame.transform.scale(img, pygame.Vector2(img.get_width() * 4, img.get_height() * 4)).convert_alpha()
        if random.randint(0, 1) == 1:
            img = pygame.transform.flip(img, True, False)

        img.set_colorkey(pygame.Color(0, 0, 0, 0))

        img = pygame.mask.from_surface(img).to_surface(
            setcolor=pygame.Color(170, 170, 170), 
            unsetcolor=pygame.Color(0, 0, 0, 0)
        )

        super().__init__(position, img, dimensions, strata, dist=80)
        
        self.base_strata = strata
        self.offset = pygame.Vector2(0, 8)

        self.outline = False

    def on_select(self):
        self.selected = True
        self.outline = True

    def on_interact(self, interacter):
        if get_distance(interacter, self) > self.interact_dist:
            return False

        self.interacter = interacter
        self.interacting = True

        self.strata = interacter.strata + 1
        
        return True

    def on_release(self):
        self.interacter = None
        self.interacting = False
        self.strata = self.base_strata

    def apply_gravity(self, dt):
        if not self.collide_points['bottom']:
            self.velocity.y += GRAVITY * dt if self.velocity.y < MAX_GRAVITY * dt else 0

        else:
            self.velocity.y = GRAVITY * dt

    def apply_collision_x(self, scene):
        self.collide_points['right'] = False
        self.collide_points['left'] = False

        collidables = [s for s in scene.sprites if isinstance(s, Tile)]

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

        self.apply_collision_y_default([s for s in scene.sprites if isinstance(s, Platform) or isinstance(s, Tile)])

        ramps = [s for s in scene.sprites if isinstance(s, Ramp)]
        for ramp in ramps:
            if not self.rect.colliderect(ramp.rect):
                continue

            pos = ramp.get_y_value(self)

            if pos - self.rect.bottom < 4:
                self.collide_points['bottom'] = True
                self.rect.bottom = pos
                self.velocity.y = 0
        
    def apply_interact_effect(self, player):
        player.velocity.x = round(player.velocity.x * .75)

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

        if self.outline:
            create_outline(self, COLOR_VALUES_SECONDARY[scene.player.color], scene.entity_surface, 4)
            self.outline = False

        scene.entity_surface.blit(self.image, self.rect)
        self.selected = False