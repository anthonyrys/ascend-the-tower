from scripts.constants import ENEMY_COLOR
from scripts.engine import Entity, SpriteMethods

from scripts.core_systems.combat_handler import Combat
from scripts.core_systems.enemy_ai import Flyer
from scripts.core_systems.level_handler import Level

from scripts.entities.particle_fx import Circle, Experience

from scripts.ui.enemybar import Enemybar

import pygame
import random
import math
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
            'max_health': 100,
            'health': 100,

            'contact_damage': 0,
            'crit_strike_chance': 0,
            'crit_strike_multiplier': 0,

            'knockback_resistance': 1,
            
            'immunities': Combat.get_immunity_dict(),
            'mitigations': {}
        }

        self.level_info = {
            'level': 0,
            'experience_amount': 0,
            'experience_multiplier': 1,
            'health_scaling': 1.0,
            'damage_scaling': 1.0,
            'crit_chance_scaling': 1.0,
            'crit_multiplier_scaling': 1.0
        }

        self.img_info = {
            'damage_frames': 0,
            'damage_frames_max': 0
        }

    def on_death(self, scene, info):
        amount = Level.calculate_experience(self.level_info['level'], self.level_info['experience_multiplier'])
        
        particles = []
        for _ in range(self.level_info['experience_amount']):
            exp = Experience(self.rect.center, (166, 225, 136), 5, 0, round(amount / self.level_info['experience_amount']))
            exp.glow['active'] = True
            exp.glow['intensity'] = .15
            
            exp.set_goal(25, position=[
                self.rect.centerx + random.randint(-50, 50),
                self.rect.centery + random.randint(-50, 50)
            ])

            particles.append(exp)

        scene.add_sprites(particles)

    def set_stats(self):
        self.combat_info['max_health'] = round(math.pow(self.combat_info['max_health'] * (self.level_info['level']), self.level_info['health_scaling']))
        self.combat_info['health'] = self.combat_info['max_health']

        self.combat_info['contact_damage'] = round(math.pow(self.combat_info['contact_damage'] * (self.level_info['level']), self.level_info['damage_scaling']))
        self.combat_info['crit_strike_chance'] = round(math.pow(self.combat_info['crit_strike_chance'] * (self.level_info['level']), self.level_info['crit_chance_scaling']), 2)
        self.combat_info['crit_strike_multiplier'] = round(math.pow(self.combat_info['crit_strike_multiplier'] * (self.level_info['level']), self.level_info['crit_multiplier_scaling']), 2)

    def display(self, scene, dt):
        super().display(scene, dt)       
        if self.img_info['damage_frames'] > 0:
            img = self.mask.to_surface(
                setcolor=ENEMY_COLOR,
                unsetcolor=(0, 0, 0, 0)
            )

            img.set_alpha(255 * (self.img_info['damage_frames'] / self.img_info['damage_frames_max'])) 
            scene.entity_surface.blit(img, (self.rect.x - self.rect_offset[0], self.rect.y - self.rect_offset[1]))

            self.img_info['damage_frames'] -= 1 * dt

class Stelemental(Enemy):
    def __init__(self, position, strata):
        img_scale = 2.5
        img = pygame.image.load(os.path.join('imgs', 'entities', 'enemies', 'stelemental.png'))
        img = pygame.transform.scale(img, (img.get_width() * img_scale, img.get_height() * img_scale)).convert_alpha()

        super().__init__(position, img, None, strata, None)

        self.ai = Flyer(self)

        self.movement_info['friction'] = 2
        self.movement_info['base_friction'] = self.movement_info['friction'] 
        self.movement_info['per_frame_movespeed'] = .2
        self.movement_info['max_movespeed'] = 5

        self.combat_info = {
            'max_health': 100,
            'health': 100,

            'contact_damage': 30,
            'crit_strike_chance': 0,
            'crit_strike_multiplier': 0,

            'knockback_resistance': .75,
            
            'immunities': Combat.get_immunity_dict(),
            'mitigations': {}
        }

        self.level_info = {
            'level': 1,

            'experience_amount': 4,
            'experience_multiplier': 1,

            'health_scaling': .95,
            'damage_scaling': .9,
            'crit_chance_scaling': 1,
            'crit_multiplier_scaling': 1
        }

        self.set_stats()
        
    def on_death(self, scene, info):
        super().on_death(scene, info)

        pos = self.center_position
        particles = []
        for color in SpriteMethods.get_sprite_colors(self, 2):
            cir = Circle(pos, color, 10, 0)
            cir.set_goal(
                        120, 
                        position=(pos[0] + random.randint(-450, 450), pos[1] + random.randint(-350, -250)), 
                        radius=0, 
                        width=0
                    )
            cir.set_gravity(7)
            cir.set_easings(radius='ease_out_sine')

            particles.append(cir)

        scene.add_sprites(particles)
        scene.del_sprites(self)

    def on_damaged(self, scene, sprite, info):
        if 'velocity' in info:
            info_velocity = info['velocity']
            self.velocity[0] = info_velocity[0]
            
            if info_velocity[1] >= 0:
                self.velocity[1] = info_velocity[1]
            elif sprite.velocity[1] < 0:
                self.velocity[1] = -info_velocity[1]

            self.velocity[0] = round(self.velocity[0] * self.combat_info['knockback_resistance'], 1)
            self.velocity[1] = round(self.velocity[1] * self.combat_info['knockback_resistance'], 1) * .5

        self.img_info['damage_frames'] = 10
        self.img_info['damage_frames_max'] = 10

        pos = self.center_position
        particles = []
        for color in SpriteMethods.get_sprite_colors(self):
            cir = Circle(pos, color, 10, 0)
            cir.set_goal(
                        100, 
                        position=(pos[0] + random.randint(-350, 350), pos[1] + random.randint(-350, 350)), 
                        radius=0, 
                        width=0
                    )
            cir.set_gravity(5)
            cir.set_easings(radius='ease_out_sine')

            particles.append(cir)
        scene.add_sprites(particles)

        if not info['crit']:
            self.health_ui.set_pulse(10, (225, 225, 225))
        else:
            self.health_ui.set_pulse(10, (251, 204, 97))

    def on_contact(self, scene, dt):
        Combat.register_damage(
            scene,
            self,
            scene.player,
            {'type': 'contact', 'amount': self.combat_info['contact_damage'], 'velocity': None}
        )

    def display(self, scene, dt):
        self.ai.update(scene, dt, scene.player)

        if SpriteMethods.check_pixel_collision(self, scene.player):
            self.on_contact(scene, dt)

        SpriteMethods.create_outline_edge(self, ENEMY_COLOR, scene.entity_surface, 3)

        if self.combat_info['health'] < self.combat_info['max_health']:
            self.health_ui.display(scene, dt)

        super().display(scene, dt)
