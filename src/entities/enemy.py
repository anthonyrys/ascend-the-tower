from src.engine import Entity, SpriteMethods

from src.core_systems.combat_handler import CombatMethods
from src.core_systems.enemy_ai import Flyer

from src.ui.enemybar import Enemybar

import pygame
import os

class Enemy(Entity):
    def __init__(self, position, img, dimensions, strata, alpha):
        super().__init__(position, img, dimensions, strata, alpha)

        self.ai = None
        self.health_ui = Enemybar(self)

        self.movement_info = {
            'direction': None,

            'friction': None,
            'base_friction': None,
            'friction_frames': None,

            'per_frame_movespeed': None,
            'max_movespeed': None,

            'jump_power': None,
            'jumps': None,
            'max_jumps': None
        }

        self.combat_info = {
            'max_health': None,
            'health': None,

            'contact_damage': None,
            'knockback_resistance': None
        }

        self.immunities = {}

    def display(self, scene, dt):
        super().display(scene, dt)

class Stelemental(Enemy):
    def __init__(self, position, strata):
        img_scale = 2.5
        img = pygame.image.load(os.path.join('imgs', 'enemies', 'stelemental.png'))
        img = pygame.transform.scale(img, (img.get_width() * img_scale, img.get_height() * img_scale))

        super().__init__(position, img, None, strata, None)

        self.ai = Flyer(self)

        self.movement_info['per_frame_movespeed'] = .2
        self.movement_info['max_movespeed'] = 5
        self.movement_info['friction'] = 2

        self.combat_info['contact_damage'] = 15
        self.combat_info['max_health'] = 100
        self.combat_info['health'] = self.combat_info['max_health']
        self.combat_info['knockback_resistance'] = .65

    def on_damaged(self, scene, sprite, info):
        info_velocity = info['velocity']
        self.velocity[0] = info_velocity[0]
        
        if info_velocity[1] >= 0:
            self.velocity[1] = info_velocity[1]
        elif sprite.velocity[1] < 0:
            self.velocity[1] = -info_velocity[1]

        self.velocity[0] = round(self.velocity[0] * self.combat_info['knockback_resistance'], 1)
        self.velocity[1] = round(self.velocity[1] * self.combat_info['knockback_resistance'], 1) * .5

    def on_contact(self, scene, dt):
        CombatMethods.register_damage(
            scene,
            self,
            scene.player,
            {'type': 'contact', 'amount': self.combat_info['contact_damage'], 'velocity': None}
        )

    def display(self, scene, dt):
        self.ai.update(scene, dt, scene.player)

        if SpriteMethods.check_pixel_collision(self, scene.player):
            self.on_contact(scene, dt)

        SpriteMethods.create_outline_edge(self, (242, 59, 76), scene.entity_surface, 3)

        if self.combat_info['health'] < self.combat_info['max_health']:
            self.health_ui.display(scene, dt)

        super().display(scene, dt)
    