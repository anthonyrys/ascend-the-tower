from src.constants import (
    GRAVITY,
    MAX_GRAVITY,
    COLOR_VALUES_SECONDARY
)

from src.engine import (
    get_distance,
    create_outline
)

from src.entities.interactable import Interactable
from src.entities.tile import Tile
from src.entities.platform import Platform
from src.entities.ramp import Ramp

import pygame

class Block(Interactable):
    def __init__(self, position, dimensions, strata):
        super().__init__(position, (235, 235, 235), dimensions, strata, dist=80)
        
        self.base_strata = strata
        self.offset = (0, 8)

        self.outline = False

    def on_select(self):
        self.selected = True

    def on_interact(self, scene, interacter):
        if get_distance(interacter, self) > self.interact_dist:
            return False

        self.interacter = interacter
        self.interacting = True
        self.selected = False

        self.strata = interacter.strata + 1
    
        return True

    def on_release(self):
        self.interacter = None
        self.interacting = False

    def apply_gravity(self, dt):
        if not self.collide_points['bottom']:
            self.velocity[1] += GRAVITY * dt if self.velocity[1] < MAX_GRAVITY * dt else 0

        else:
            self.velocity[1] = GRAVITY * dt

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
                self.velocity[1] = 0
        
    def apply_interact_effect(self, player):
        player.velocity[0] = round(player.velocity[0] * .75)

    def display(self, scene, dt):
        if scene.paused:
            super().display(scene, dt)
            return

        if not self.interacting:
            if self.strata != self.base_strata:
                self.strata = self.base_strata
                
            self.apply_gravity(dt)

            self.rect.x += self.velocity[0] * dt
            self.apply_collision_x(scene)

            self.rect.y += self.velocity[1] * dt
            self.apply_collision_y(scene)

        else:
            direction = self.interacter.rect.left if self.interacter.direction < 0 else self.interacter.rect.right
            center = self.interacter.mask.centroid()[1]

            self.rect.center = (
                self.offset[0] + direction, 
                self.offset[1] + self.interacter.rect.centery + (center - self.image.get_height())
            )

        if self.selected:
            create_outline(self, COLOR_VALUES_SECONDARY[scene.player.color], scene.entity_surface, 4)
            self.selected = False

        super().display(scene, dt)