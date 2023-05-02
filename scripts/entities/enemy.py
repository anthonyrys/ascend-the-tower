'''
Holds the enemy baseclass as well as enemy subclasses.
'''

from scripts.constants import ENEMY_COLOR, CRIT_COLOR
from scripts.engine import get_sprite_colors, check_pixel_collision, check_line_collision, create_outline_edge, get_distance

from scripts.core_systems.combat_handler import get_immunity_dict, get_mitigation_dict, register_damage
from scripts.core_systems.enemy_ai import Flyer
from scripts.core_systems.abilities import Ability

from scripts.entities.game_entity import GameEntity
from scripts.entities.particle_fx import Circle, Image
from scripts.entities.projectile import ProjectileStandard

from scripts.ui.info_bar import EnemyBar
from scripts.ui.text_box import TextBox

import pygame
import random
import math
import os

class Enemy(GameEntity):
    '''
    Enemy baseclass, intended to be inherited from.

    Variables:
        ai: ai object used to control the enemy.
        health_ui: InfoBar object to display enemy information (health).
        variant: determines whether the enemy should use special features.

        level_info: information used to determine the strength of the enemy.
        img_info: information on how the enemy images should be displayed.

        abilities: a list of abilities that the entity can use.
        ability_info: information on how the enemy abilities should function.

    Methods:
        on_death(): called when the enemy has died.
        on_damaged(): called when the enemy has been damaged.
        set_stats(): sets the enemy stats using the level_info.

        variant_display(): addition to the regular display that calls for variant enemies.
    '''

    def __init__(self, position, img, dimensions, strata, alpha, variant):
        super().__init__(position, img, dimensions, strata, alpha)

        self.sprite_id = 'enemy'
        
        self.ai = None
        self.health_ui = EnemyBar(self)
        self.variant = variant

        self.level_info = {
            'level': 0,

            'health_scaling': 1.0,
            'damage_scaling': 1.0,
            'crit_chance_scaling': 1.0,
            'crit_multiplier_scaling': 1.0
        }

        self.img_info = {
            'damage_frames': 0,
            'damage_frames_max': 0
        }

        self.abilities = []
        self.ability_info = {}

    def on_death(self, scene, info):
        ...

    def on_damaged(self, scene, info):
        color = (225, 225, 225)
        size = .5

        if info['crit']:
           color = CRIT_COLOR
           size = .6
            
        img = TextBox((0, 0), info['amount'], color=color, size=size).image.copy()

        particle = Image(self.rect.center, img, 6, 255)
        particle.set_easings(alpha='ease_in_quint')
    
        particle.set_goal(
            30, 
            position=(self.rect.centerx + random.randint(-50, 50), particle.rect.centery + random.randint(-50, 50)),
            alpha=0,
            dimensions=(img.get_width(), img.get_height())
        )

        scene.add_sprites(particle)

    def on_ability(self, scene, dt):
        ...

    def set_stats(self):
        self.combat_info['max_health'] = round(math.pow(self.combat_info['max_health'] * (self.level_info['level']), self.level_info['health_scaling']))
        self.combat_info['health'] = self.combat_info['max_health']

        self.combat_info['base_damage'] = round(math.pow(self.combat_info['base_damage'] * (self.level_info['level']), self.level_info['damage_scaling']))
        self.combat_info['crit_strike_chance'] = round(math.pow(self.combat_info['crit_strike_chance'] * (self.level_info['level']), self.level_info['crit_chance_scaling']), 2)
        self.combat_info['crit_strike_multiplier'] = round(math.pow(self.combat_info['crit_strike_multiplier'] * (self.level_info['level']), self.level_info['crit_multiplier_scaling']), 2)

    def variant_display(self, scene, dt):
        ...

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
    class Blast(Ability):
        def __init__(self, character):
            super().__init__(character)
        
            self.ability_info['damage'] = character.combat_info['base_damage'] * 2.5
            self.ability_info['speed'] = 15

        def collision_default(self, scene, projectile, sprite):
            particles = []
            pos = projectile.center_position

            for _ in range(3):
                cir = Circle(pos, projectile.color, 5, 0)
                cir.set_goal(
                            75, 
                            position=(
                                pos[0] + random.randint(-75, 75) + (projectile.velocity[0] * 10), 
                                pos[1] + random.randint(-75, 75) + (projectile.velocity[1] * 10)
                            ), 
                            radius=0, 
                            width=0
                        )

                cir.glow['active'] = True
                cir.glow['size'] = 1.25
                cir.glow['intensity'] = .25

                particles.append(cir)
                
            scene.add_sprites(particles)

        def collision_player(self, scene, projectile, sprite):
            self.collision_default(scene, projectile, sprite)
            register_damage(scene, self.character, sprite, {'type': 'magical', 'amount': self.ability_info['damage']})

        def call(self, scene, keybind=None):
            player = scene.player
            dist = get_distance(self.character, player)

            proj_velocity = [
                round((player.rect.x - self.character.rect.x) / (dist / self.ability_info['speed'])),
                round((player.rect.y - self.character.rect.y) / (dist / self.ability_info['speed']))
            ]

            proj_info = {
                'collision': 'pixel',
                'collision_exclude': ['particle', 'projectile', 'enemy'],
                'collision_function': {
                    'player': self.collision_player,
                    'default': self.collision_default
                },

                'duration': 90
            }

            proj = ProjectileStandard(
                self.character.rect.center, ENEMY_COLOR, 10, self.character.strata + 1,
                proj_info,
                velocity=proj_velocity, 
                trail=True, 
                afterimages=True
            )

            particles = []
            for _ in range(5):
                cir = Circle(self.character.rect.center, ENEMY_COLOR, 6, 0)
                cir.set_goal(
                            50, 
                            position=(
                                self.character.rect.center[0] + random.randint(-50, 50) + (proj_velocity[0] * 15), 
                                self.character.rect.center[1] + random.randint(-50, 50) + (proj_velocity[1] * 15)
                            ), 
                            radius=0, 
                            width=0
                        )

                cir.glow['active'] = True
                cir.glow['size'] = 1.25
                cir.glow['intensity'] = .25

                particles.append(cir)

            scene.add_sprites(particles)
            scene.add_sprites(proj)

    def __init__(self, position, strata, variant=False):
        enemy_name = 'stelemental'

        img = None
        img_scale = 2.5

        if variant:
            img = pygame.image.load(os.path.join('imgs', 'entities', 'enemies', enemy_name, f'{enemy_name}-variant.png'))
        else:
            img = pygame.image.load(os.path.join('imgs', 'entities', 'enemies', enemy_name, f'{enemy_name}.png'))

        img = pygame.transform.scale(img, (img.get_width() * img_scale, img.get_height() * img_scale)).convert_alpha()

        super().__init__(position, img, None, strata, None, variant)

        self.secondary_sprite_id = enemy_name
        self.ai = Flyer(self)

        self.default_movement_info = {
            'direction': 0,

            'friction': 2,
            'friction_frames': 0,

            'per_frame_movespeed': .2,
            'max_movespeed': 5,

            'jump_power': 24,
            'jumps': 0,
            'max_jumps': 2
        }

        self.movement_info = self.default_movement_info.copy()

        self.default_combat_info = {
            'max_health': 75,
            'health': 75,
            
            'health_regen_amount': 0,
            'health_regen_tick': 0,
            'health_regen_timer': 0,

            'damage_multiplier': 1.0,
            'healing_multiplier': 1.0,

            'base_damage': 30,
            'crit_strike_chance': 0,
            'crit_strike_multiplier': 0,

            'knockback_resistance': .75,
            
            'immunities': get_immunity_dict(),
            'mitigations': get_mitigation_dict()
        }

        self.combat_info = self.default_combat_info.copy()

        if self.variant:
            self.combat_info['max_health'] = 125
            self.combat_info['health'] = 125
            self.combat_info['base_damage'] = 15

            self.ability_info['activation_frames'] = [0, 60]

            self.ability_info['activation_charge_up_percentage'] = .66
            self.ability_info['activation_charge_up'] = False

        self.level_info = {
            'level': 1,

            'health_scaling': .95,
            'damage_scaling': .9,
            'crit_chance_scaling': 1,
            'crit_multiplier_scaling': 1
        }

        self.set_stats()

        self.abilities.append(self.Blast(self))
        
    def on_death(self, scene, info):
        super().on_death(scene, info)

        pos = self.center_position
        particles = []
        for color in get_sprite_colors(self, 2):
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

    def on_damaged(self, scene, info):
        super().on_damaged(scene, info)

        sprite = info['primary']

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
        for color in get_sprite_colors(self):
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
            self.health_ui.set_pulse(10, CRIT_COLOR)

        if self.variant:
            self.ability_info['activation_frames'][0] = random.randint(0, 5)
            self.ability_info['activation_charge_up'] = False

    def on_contact(self, scene, dt):
        register_damage(
            scene,
            self,
            scene.player,
            {'type': 'contact', 'amount': self.combat_info['base_damage'], 'velocity': None}
        )
    
    def variant_display(self, scene, dt):
        if check_line_collision(scene.player.rect.center, self.rect.center, scene.sprites, ['player', 'enemy', 'particle', 'projectile']):
            self.ability_info['activation_frames'][0] = random.randint(0, 5)
            self.ability_info['activation_charge_up'] = False
            return
        
        self.ability_info['activation_frames'][0] += 1 * dt

        charge_up_frames = round(self.ability_info['activation_frames'][1] * self.ability_info['activation_charge_up_percentage'])
        if round(self.ability_info['activation_frames'][0]) == charge_up_frames and not self.ability_info['activation_charge_up']:
            self.ability_info['activation_charge_up'] = True

            frames = round(self.ability_info['activation_frames'][1]) - round(self.ability_info['activation_frames'][1] * .66)
            particle = Circle(
                [0, 0],
                ENEMY_COLOR,
                50,
                3,
                self
            )

            particle.set_goal(frames, position=[0, 0], radius=0, width=3)
            scene.add_sprites(particle)

        if self.ability_info['activation_frames'][0] >= self.ability_info['activation_frames'][1]:
            self.ability_info['activation_frames'][0] = 0
            self.ability_info['activation_charge_up'] = False

            random.choice(self.abilities).call(scene)

    def display(self, scene, dt):
        self.ai.update(scene, dt, scene.player)

        if check_pixel_collision(self, scene.player):
            self.on_contact(scene, dt)

        if self.variant:
            self.variant_display(scene, dt)
                    
        create_outline_edge(self, ENEMY_COLOR, scene.entity_surface, 3)

        if self.combat_info['health'] < self.combat_info['max_health']:
            self.health_ui.display(scene, dt)

        super().display(scene, dt)