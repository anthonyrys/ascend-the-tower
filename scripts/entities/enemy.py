'''
Holds the enemy baseclass as well as enemy subclasses.
'''

from scripts.constants import ENEMY_COLOR, CRIT_COLOR
from scripts.engine import get_sprite_colors, check_pixel_collision, get_distance, check_line_collision

from scripts.core_systems.abilities import Ability
from scripts.core_systems.combat_handler import get_immunity_dict, get_mitigation_dict, register_damage
from scripts.core_systems.enemy_ai import HumanoidAi, FlyerAi, FloaterAi

from scripts.entities.game_entity import GameEntity
from scripts.entities.particle_fx import Circle, Image
from scripts.entities.projectile import ProjectileStandard

from scripts.services.spritesheet_loader import load_spritesheet

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
        healthbar: InfoBar object to display enemy information (health).

        level_info: information used to determine the strength of the enemy.
        img_info: information on how the enemy images should be displayed.

        abilities: a list of abilities that the entity can use.
        ability_info: information on how the enemy abilities should function.

    Methods:
        on_death(): called when the enemy has died.
        on_damaged(): called when the enemy has been damaged.
        set_stats(): sets the enemy stats using the level_info.
    '''

    def __init__(self, position, img, dimensions, strata, alpha):
        super().__init__(position, img, dimensions, strata, alpha)
        self.sprite_id = 'enemy'

        self.ai = None
        self.healthbar = EnemyBar(self)

        self.level_info = {
            'level': 0,

            'max_health_scaling': 1.0,
            'base_damage_scaling': 1.0,
            'crit_strike_chance_scaling': 1.0,
            'crit_strike_multiplier_scaling': 1.0
        }

        self.img_info = {
            'damage_frames': 0,
            'damage_frames_max': 0
        }

        self.abilities = []
        self.ability_info = {}

    def on_contact(self, scene, dt):
        register_damage(
            scene,
            self,
            scene.player,
            {'type': 'contact', 'amount': self.combat_info['base_damage'], 'velocity': self.velocity}
        )
        
    def on_death(self, scene, info):
        scene.on_enemy_death(self)

        pos = self.center_position
        particles = []
        for color in get_sprite_colors(self):
            radius = round(((self.image.get_width() + self.image.get_height()) / 2) * .125)

            cir = Circle(pos, color, radius, 0)
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
        sprite = info['primary']

        if info['velocity']:
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

        if not 'minor' in info:
            pos = self.center_position
            particles = []

            for color in get_sprite_colors(self):
                radius = round(((self.image.get_width() + self.image.get_height()) / 2) * .15)

                cir = Circle(pos, color, radius, 0)
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
            self.healthbar.set_pulse(10, (225, 225, 225))
        else:
            self.healthbar.set_pulse(10, CRIT_COLOR)

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

    def set_stats(self):
        def get_stat_scaling(stat, level, scaling):
            return round(stat * (level - 1) * scaling)
        
        for stat in ['max_health', 'base_damage', 'crit_strike_chance', 'crit_strike_multiplier']:
            self.combat_info[stat] += get_stat_scaling(self.combat_info[stat], self.level_info['level'], self.level_info[f'{stat}_scaling'])

        self.combat_info['health'] = self.combat_info['max_health']

    def display(self, scene, dt):
        if self.combat_info['health'] < self.combat_info['max_health']:
            self.healthbar.display(scene, dt)

        if check_pixel_collision(self, scene.player):
            self.on_contact(scene, dt)

        super().display(scene, dt)       
        
        if self.img_info['damage_frames'] > 0:
            img = self.mask.to_surface(
                setcolor=ENEMY_COLOR,
                unsetcolor=(0, 0, 0, 0)
            )

            img.set_alpha(255 * (self.img_info['damage_frames'] / self.img_info['damage_frames_max'])) 
            scene.entity_surface.blit(img, (self.rect.x - self.rect_offset[0], self.rect.y - self.rect_offset[1]))

            self.img_info['damage_frames'] -= 1 * dt


class HumanoidEnemy(Enemy):
    def __init__(self, position, img, dimensions, strata, alpha):
        super().__init__(position, img, dimensions, strata, alpha)
        self.ai = HumanoidAi(self)

    def apply_collision_x(self, scene):
        self.collide_points['right'] = False
        self.collide_points['left'] = False

        self.apply_collision_x_default([s for s in scene.sprites if s.secondary_sprite_id in ['block', 'barrier']])

    def apply_collision_y(self, scene, dt):
        self.collide_points['top'] = False
        self.collide_points['bottom'] = False

        if 'bottom' in self.apply_collision_y_default([s for s in scene.sprites if s.secondary_sprite_id in ['block', 'barrier']]):
            if self.movement_info['jumps'] != self.movement_info['max_jumps']:
                self.movement_info['jumps'] = self.movement_info['max_jumps']

        if 'bottom' in self.apply_collision_y_default([s for s in scene.sprites if s.secondary_sprite_id in ['ceiling', 'floor']]):
            if self.movement_info['jumps'] != self.movement_info['max_jumps']:
                self.movement_info['jumps'] = self.movement_info['max_jumps']
     
        platforms = [s for s in scene.sprites if s.secondary_sprite_id == 'platform']
        for platform in platforms:
            if not self.rect.colliderect(platform.rect):
                if platform in self.collision_ignore:
                    self.collision_ignore.remove(platform)

                if platform in self.collisions:
                    self.collisions.remove(platform)

                continue

            if self.velocity[1] > 0 and self.rect.bottom <= platform.rect.top + (self.velocity[1] * dt):
                self.rect.bottom = platform.rect.top
                self.collide_points['bottom'] = True

                if platform not in self.collisions:
                    self.collisions.append(platform)

                if self.movement_info['jumps'] != self.movement_info['max_jumps']:
                    self.movement_info['jumps'] = self.movement_info['max_jumps']
                        
                self.velocity[1] = 0

class FlyerEnemy(Enemy):
    def __init__(self, position, img, dimensions, strata, alpha):
        super().__init__(position, img, dimensions, strata, alpha)
        self.ai = FlyerAi(self)

class FloaterEnemy(Enemy):
    def __init__(self, position, img, dimensions, strata, alpha):
        super().__init__(position, img, dimensions, strata, alpha)
        self.ai = FloaterAi(self)


class Humanoid(HumanoidEnemy):
    def __init__(self, position, strata, level=1):
        super().__init__(position, pygame.Surface((24, 48)).convert_alpha(), None, strata, None)
        self.secondary_sprite_id = 'humanoid'

        self.rect_offset = [self.rect.width / 2, 0]

        self.cooldown_timers['jump'] = 30

        self.default_movement_info = {
            'direction': 0,

            'friction': 2,
            'friction_frames': 0,

            'per_frame_movespeed': 1,
            'max_movespeed': 9,

            'jump_power': 24,
            'jumps': 0,
            'max_jumps': 1
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

            'base_damage': 20,
            'crit_strike_chance': 0,
            'crit_strike_multiplier': 0,

            'knockback_resistance': .75,
            
            'immunities': get_immunity_dict(),
            'mitigations': get_mitigation_dict()
        }

        self.combat_info = self.default_combat_info.copy()

        self.level_info = {
            'level': level,

            'max_health_scaling': .45,
            'base_damage_scaling': .2,
            'crit_strike_chance_scaling': 1.0,
            'crit_strike_multiplier_scaling': 1.0
        }

        self.set_stats()

        self.img_info = {
            'damage_frames': 0,
            'damage_frames_max': 0,

            'imgs': {},
            'scale': 1.5,

            'frames': {},
            'frames_raw': {},
            'frame_info': {
                'idle': [50, 50],
                'run': [2, 2, 2, 2, 2],
                'jump': [1],
                'fall': [1]
            }
        }
        
        for name in ['idle', 'run', 'jump', 'fall']:
            self.img_info['imgs'][name] = load_spritesheet(
                os.path.join('imgs', 'entities', 'enemies', self.secondary_sprite_id, f'{self.secondary_sprite_id}-{name}.png'), self.img_info['frame_info'][name]
            )

            self.img_info['frames'][name] = 0
            self.img_info['frames_raw'][name] = 0
    
    def set_images(self, scene, dt): 
        img = None
        et = 1

        if dt != 0:
            player_pos = scene.player.center_position[0]

            if player_pos > self.rect.centerx:
                self.movement_info['direction'] = 1

            elif player_pos < self.rect.centerx:
                self.movement_info['direction'] = -1

        if self.state_info['movement'] == 'run':
            et = 1 if abs(self.velocity[0] / self.movement_info['max_movespeed']) > 1 else abs(self.velocity[0] / self.movement_info['max_movespeed'])

        if len(self.img_info['imgs'][self.state_info['movement']]) <= self.img_info['frames'][self.state_info['movement']]:
            self.img_info['frames'][self.state_info['movement']] = 0
            self.img_info['frames_raw'][self.state_info['movement']] = 0

        img = self.img_info['imgs'][self.state_info['movement']][self.img_info['frames'][self.state_info['movement']]]

        self.img_info['frames_raw'][self.state_info['movement']] += (1 * et) * dt
        self.img_info['frames'][self.state_info['movement']] = round(self.img_info['frames_raw'][self.state_info['movement']])

        for frame in self.img_info['frames']:
            if self.state_info['movement'] == frame:
                continue

            self.img_info['frames'][frame] = random.randint(0, len(self.img_info['imgs'][frame]))
            self.img_info['frames_raw'][frame] = random.randint(0, len(self.img_info['imgs'][frame]))

        self.image = pygame.transform.scale(img, (img.get_width() * self.img_info['scale'], img.get_height() * self.img_info['scale'])).convert_alpha()
        self.image = pygame.transform.flip(self.image, True, False).convert_alpha() if self.movement_info['direction'] < 0 else self.image

    def display(self, scene, dt):
        if not scene.paused:
            self.apply_gravity(dt)
            self.ai.update(scene, dt, scene.player)

            if abs(self.velocity[0]) < self.movement_info['per_frame_movespeed']:
                self.velocity[0] = 0

            self.rect.x += round(self.velocity[0] * dt)
            self.apply_collision_x(scene)

            self.rect.y += round(self.velocity[1] * dt)
            self.apply_collision_y(scene, dt)

            self.set_frame_state()

        self.set_images(scene, dt)
        super().display(scene, dt)

class Flyer(FlyerEnemy):
    def __init__(self, position, strata, level=1):
        super().__init__(position, pygame.Surface((64, 64)).convert_alpha(), None, strata, None)
        self.secondary_sprite_id = 'flyer'

        self.default_movement_info = {
            'direction': 0,

            'friction': 2,
            'friction_frames': 0,

            'per_frame_movespeed': .4,
            'max_movespeed': 15,

            'jump_power': 24,
            'jumps': 0,
            'max_jumps': 1
        }

        self.movement_info = self.default_movement_info.copy()

        self.default_combat_info = {
            'max_health': 60,
            'health': 60,
            
            'health_regen_amount': 0,
            'health_regen_tick': 0,
            'health_regen_timer': 0,

            'damage_multiplier': 1.0,
            'healing_multiplier': 1.0,

            'base_damage': 25,
            'crit_strike_chance': 0,
            'crit_strike_multiplier': 0,

            'knockback_resistance': .75,
            
            'immunities': get_immunity_dict(),
            'mitigations': get_mitigation_dict()
        }

        self.combat_info = self.default_combat_info.copy()

        self.level_info = {
            'level': level,

            'max_health_scaling': .35,
            'base_damage_scaling': .25,
            'crit_strike_chance_scaling': 1.0,
            'crit_strike_multiplier_scaling': 1.0
        }

        self.set_stats()

        self.img_info = {
            'damage_frames': 0,
            'damage_frames_max': 0,

            'img': None
        }

        img = pygame.image.load(os.path.join('imgs', 'entities', 'enemies', self.secondary_sprite_id, f'{self.secondary_sprite_id}.png')).convert_alpha()
        img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))

        self.img_info['img'] = img
    
    def set_images(self, scene, dt):
        self.image.fill((0, 0, 0, 0))

        pos_x = self.center_position[0] + self.velocity[0] * 10
        pos_y = self.center_position[1] + self.velocity[1] * 10

        angle = (180 / math.pi) * math.atan2(pos_x - self.center_position[0], pos_y - self.center_position[1])

        img = self.img_info['img'].copy()
        img = pygame.transform.rotate(img, angle)

        self.image.blit(img, img.get_rect(center=self.image.get_rect().center))

    def display(self, scene, dt):
        if not scene.paused:
            self.ai.update(scene, dt, scene.player)

            if abs(self.velocity[0]) < self.movement_info['per_frame_movespeed']:
                self.velocity[0] = 0

            self.rect.x += round(self.velocity[0] * dt)
            self.rect.y += round(self.velocity[1] * dt)

        self.set_images(scene, dt)
        super().display(scene, dt)

class Floater(FloaterEnemy):
    class Blast(Ability):
        def __init__(self, character):
            super().__init__(character)
        
            self.ability_info['damage_multiplier'] = 1.25
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
            register_damage(scene, self.character, sprite, {
                'type': 'magical', 
                'amount': self.character.combat_info['base_damage'] * self.ability_info['damage_multiplier']})

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

    def __init__(self, position, strata, level=1):
        super().__init__(position, pygame.Surface((64, 64)).convert_alpha(), None, strata, None)
        self.secondary_sprite_id = 'floater'

        self.default_movement_info = {
            'direction': 0,

            'friction': 2,
            'friction_frames': 0,

            'per_frame_movespeed': .5,
            'max_movespeed': 6,

            'jump_power': 1,
            'jumps': 0,
            'max_jumps': 1
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

            'base_damage': 25,
            'crit_strike_chance': 0,
            'crit_strike_multiplier': 0,

            'knockback_resistance': .9,
            
            'immunities': get_immunity_dict(),
            'mitigations': get_mitigation_dict()
        }

        self.combat_info = self.default_combat_info.copy()

        self.level_info = {
            'level': level,

            'max_health_scaling': .35,
            'base_damage_scaling': .25,
            'crit_strike_chance_scaling': 1.0,
            'crit_strike_multiplier_scaling': 1.0
        }

        self.set_stats()

        self.img_info = {
            'damage_frames': 0,
            'damage_frames_max': 0,

            'img': None
        }

        img = pygame.image.load(os.path.join('imgs', 'entities', 'enemies', self.secondary_sprite_id, f'{self.secondary_sprite_id}.png')).convert_alpha()
        img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))

        self.img_info['img'] = img

        self.ability_info = {
            'activation_frames': [0, 60],
            'activation_charge_up_percentage': .66,
            'activation_charge_up': False
        }

        self.abilities.append(self.Blast(self))

    def on_damaged(self, scene, info):
        super().on_damaged(scene, info)

        self.ability_info['activation_frames'][0] = random.randint(0, 5)
        self.ability_info['activation_charge_up'] = False

    def set_images(self, scene, dt):
        self.image.fill((0, 0, 0, 0))

        img = self.img_info['img'].copy()
        self.image.blit(img, img.get_rect(center=self.image.get_rect().center))

    def display(self, scene, dt):
        if scene.paused:
            self.set_images(scene, dt)
            super().display(scene, dt)
            return

        if check_line_collision(scene.player.rect.center, self.rect.center, scene.sprites, ['player', 'enemy', 'particle', 'projectile']):
            self.ability_info['activation_frames'][0] = random.randint(0, 5)
            self.ability_info['activation_charge_up'] = False
        
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

        self.ai.update(scene, dt, scene.player)
        self.apply_gravity(dt, .25)

        if abs(self.velocity[0]) < self.movement_info['per_frame_movespeed']:
            self.velocity[0] = 0

        self.rect.x += round(self.velocity[0] * dt)
        self.rect.y += round(self.velocity[1] * dt)

        self.set_images(scene, dt)
        super().display(scene, dt)
