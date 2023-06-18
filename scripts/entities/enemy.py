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
        for color in get_sprite_colors(self, .5):
            radius = round(((self.image.get_width() + self.image.get_height()) / 2) * round(random.uniform(.06, .11), 2))

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

            for color in get_sprite_colors(self, .75):
                radius = round(((self.image.get_width() + self.image.get_height()) / 2) * round(random.uniform(.05, .1), 2))

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

        self.apply_collision_x_default(scene.get_sprites('tile', include=['block', 'barrier']))

    def apply_collision_y(self, scene, dt):
        self.collide_points['top'] = False
        self.collide_points['bottom'] = False

        if 'bottom' in self.apply_collision_y_default(scene.get_sprites('tile', include=['block', 'barrier'])):
            if self.movement_info['jumps'] != self.movement_info['max_jumps']:
                self.movement_info['jumps'] = self.movement_info['max_jumps']

        if 'bottom' in self.apply_collision_y_default(scene.get_sprites('tile', include=['ceiling', 'floor'])):
            if self.movement_info['jumps'] != self.movement_info['max_jumps']:
                self.movement_info['jumps'] = self.movement_info['max_jumps']
     
        platforms = scene.get_sprites('tile', 'platform')
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

        self.apply_collision_y_ramp(scene.get_sprites('tile', 'ramp'))

class FlyerEnemy(Enemy):
    def __init__(self, position, img, dimensions, strata, alpha):
        super().__init__(position, img, dimensions, strata, alpha)
        self.ai = FlyerAi(self)

class FloaterEnemy(Enemy):
    def __init__(self, position, img, dimensions, strata, alpha):
        super().__init__(position, img, dimensions, strata, alpha)
        self.ai = FloaterAi(self)


class RockGolem(HumanoidEnemy):
    def __init__(self, position, strata, level=1):
        super().__init__(position, pygame.Surface((40, 80)).convert_alpha(), None, strata, None)
        self.secondary_sprite_id = 'rgolem'

        self.rect_offset = [self.rect.width / 2, 0]

        self.cooldown_timers['jump'] = 30

        self.default_movement_info = {
            'direction': 0,

            'friction': 2,
            'friction_frames': 0,

            'per_frame_movespeed': 1,
            'max_movespeed': 7,

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

            'max_health_scaling': .65,
            'base_damage_scaling': .1,
            'crit_strike_chance_scaling': 1.0,
            'crit_strike_multiplier_scaling': 1.0
        }

        self.set_stats()

        self.img_info = {
            'damage_frames': 0,
            'damage_frames_max': 0,

            'imgs': {},
            'scale': 2.5,

            'frames': {},
            'frames_raw': {},
            'frame_info': {
                'idle': [50, 50],
                'run': [3, 3, 3, 3, 3],
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

class StoneSentry(FlyerEnemy):
    def __init__(self, position, strata, level=1):
        super().__init__(position, pygame.Surface((96, 96)).convert_alpha(), None, strata, None)
        self.secondary_sprite_id = 'stentry'

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

            'max_health_scaling': .55,
            'base_damage_scaling': .15,
            'crit_strike_chance_scaling': 1.0,
            'crit_strike_multiplier_scaling': 1.0
        }

        self.set_stats()

        self.img_info = {
            'scale': 2.5,

            'damage_frames': 0,
            'damage_frames_max': 0,

            'afterimage_frames': [0, 1],
            'imgs': []
        }

        self.img_info['imgs'] = load_spritesheet(os.path.join('imgs', 'entities', 'enemies', self.secondary_sprite_id, f'{self.secondary_sprite_id}.png'))
    
    def set_images(self, scene, dt):
        self.image.fill((0, 0, 0, 0))

        pos_x = self.center_position[0] + self.velocity[0] * 10
        pos_y = self.center_position[1] + self.velocity[1] * 10

        angle = (180 / math.pi) * math.atan2(pos_x - self.center_position[0], pos_y - self.center_position[1])

        average_vel = (abs(self.velocity[0]) + abs(self.velocity[1])) *.5
        average_vel = 1 if average_vel == 0 else average_vel

        index = round(((average_vel / (self.movement_info['max_movespeed']  * .75))) * len(self.img_info['imgs'])) - 1
        index = len(self.img_info['imgs']) - 1 if index > len(self.img_info['imgs']) - 1 else index

        img = self.img_info['imgs'][index].copy()
        img = pygame.transform.rotate(img, angle)

        img = pygame.transform.scale(img, (img.get_width() * self.img_info['scale'], img.get_height() * self.img_info['scale']))

        self.image.blit(img, img.get_rect(center=self.image.get_rect().center))

    def apply_afterimages(self, scene, dt, visuals=True):
        average_vel = (abs(self.velocity[0]) + abs(self.velocity[1])) *.5
        average_vel = 1 if average_vel == 0 else average_vel

        index = round(((average_vel / (self.movement_info['max_movespeed']  * .75))) * len(self.img_info['imgs'])) - 1
        index = len(self.img_info['imgs']) - 1 if index > len(self.img_info['imgs']) - 1 else index

        if index < len(self.img_info['imgs']) - 2:
            return
        
        self.img_info['afterimage_frames'][0] += 1 * dt
        if self.img_info['afterimage_frames'][0] < self.img_info['afterimage_frames'][1]:
            return
        
        self.img_info['afterimage_frames'][0] = 0
        
        afterimage = Image(
            self.center_position,
            self.image.copy(), self.strata - 1, 50
        )
        
        afterimage.set_goal(5, alpha=0, dimensions=self.image.get_size())

        scene.add_sprites(afterimage)

    def display(self, scene, dt):
        if not scene.paused:
            self.ai.update(scene, dt, scene.player)

            if abs(self.velocity[0]) < self.movement_info['per_frame_movespeed']:
                self.velocity[0] = 0

            self.rect.x += round(self.velocity[0] * dt)
            self.rect.y += round(self.velocity[1] * dt)

        self.set_images(scene, dt)
        self.apply_afterimages(scene, dt)
        super().display(scene, dt)

class GraniteElemental(FloaterEnemy):
    class Blast(Ability):
        def __init__(self, character):
            super().__init__(character)
        
            self.ability_info['damage_multiplier'] = 1.2
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
            if self.character.ability_info['activation_cancel']:
                return
            
            player = scene.player

            direction = [
                player.center_position[0] - self.character.center_position[0],
                player.center_position[1] - self.character.center_position[1]
            ]
            multiplier = self.ability_info['speed'] / math.sqrt(math.pow(direction[0], 2) + math.pow(direction[1], 2))
            vel = [direction[0] * multiplier, direction[1] * multiplier]

            proj_info = {
                'collision': 'pixel',
                'collisions': ['player', 'tile'],
                'collision_function': {
                    'player': self.collision_player,
                    'default': self.collision_default
                }
            }

            proj = ProjectileStandard(
                self.character.center_position, ENEMY_COLOR, 10, self.character.strata + 1,
                proj_info,
                velocity=vel,
                duration=90,
                settings={
                    'trail': True
                }
            )

            particles = []
            for _ in range(5):
                cir = Circle(self.character.center_position, ENEMY_COLOR, 6, 0)
                cir.set_goal(
                            50, 
                            position=(
                                self.character.rect.center[0] + random.randint(-50, 50) + (vel[0] * 15), 
                                self.character.rect.center[1] + random.randint(-50, 50) + (vel[1] * 15)
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
        super().__init__(position, pygame.Surface((96, 96)).convert_alpha(), None, strata, None)
        self.secondary_sprite_id = 'grelemental'

        self.image.fill((0, 0, 0, 0))
        img = pygame.image.load(os.path.join('imgs', 'entities', 'enemies', self.secondary_sprite_id, f'{self.secondary_sprite_id}.png')).convert_alpha()
        img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
        self.image.blit(img, img.get_rect(center=self.image.get_rect().center))

        self.default_movement_info = {
            'direction': 0,

            'friction': 2,
            'friction_frames': 0,

            'per_frame_movespeed': .5,
            'max_movespeed': 4,

            'jump_power': 1,
            'jumps': 0,
            'max_jumps': 1
        }

        self.movement_info = self.default_movement_info.copy()

        self.default_combat_info = {
            'max_health': 100,
            'health': 100,
            
            'health_regen_amount': 0,
            'health_regen_tick': 0,
            'health_regen_timer': 0,

            'damage_multiplier': 1.0,
            'healing_multiplier': 1.0,

            'base_damage': 25,
            'crit_strike_chance': 0,
            'crit_strike_multiplier': 0,

            'knockback_resistance': .5,
            
            'immunities': get_immunity_dict(),
            'mitigations': get_mitigation_dict()
        }

        self.combat_info = self.default_combat_info.copy()

        self.level_info = {
            'level': level,

            'max_health_scaling': .55,
            'base_damage_scaling': .1,
            'crit_strike_chance_scaling': 1.0,
            'crit_strike_multiplier_scaling': 1.0
        }

        self.set_stats()

        self.img_info = {
            'damage_frames': 0,
            'damage_frames_max': 0,

            'sin_count': 0,
            'sin_amplifier': .01,

            'size': 10,
            'color': ENEMY_COLOR,

            'radius': 65,
            'angle': 0,
            'position': [0, 0],

            'angle_speed': 3
        }

        self.ability_info = {
            'activation_frames': [0, 60],
            'activation_cancel': False
        }

        self.abilities.append(self.Blast(self))

    def on_damaged(self, scene, info):
        super().on_damaged(scene, info)

        self.ability_info['activation_frames'][0] = random.randint(0, 5)
        self.ability_info['activation_cancel'] = True

    def set_images(self, scene, dt):
        self.img_info['sin_count'] += 1 * dt

        self.img_info['angle'] += self.img_info['angle_speed'] * dt

        a = (self.img_info['angle'] - 90) * math.pi / 180
        x = self.img_info['radius'] * math.cos(a)
        y = self.img_info['radius'] * math.sin(a)

        pos = [
            self.center_position[0] + x,
            self.center_position[1] + y
        ]

        self.img_info['position'] = pos

        pygame.draw.circle(scene.entity_surface, self.img_info['color'], pos, self.img_info['size'])

        for i in range(7):
            ab = ((self.img_info['angle'] - self.img_info['angle_speed'] * (i + 2)) - 90) * math.pi / 180
            xb = self.img_info['radius'] * math.cos(ab)
            yb = self.img_info['radius'] * math.sin(ab)

            posb = [
                self.center_position[0] + xb,
                self.center_position[1] + yb
            ]

            pygame.draw.circle(scene.entity_surface, self.img_info['color'], posb, (self.img_info['size'] - (i + 1)))

    def display(self, scene, dt):
        if scene.paused:
            self.set_images(scene, dt)
            super().display(scene, dt)
            return

        if check_line_collision(scene.player.rect.center, self.rect.center, scene.get_sprites('tile', exclude='ramp')):
            self.ability_info['activation_frames'][0] = random.randint(0, 5)
        
        self.ability_info['activation_frames'][0] += 1 * dt

        if self.ability_info['activation_frames'][0] >= self.ability_info['activation_frames'][1]:
            self.ability_info['activation_cancel'] = False
            self.ability_info['activation_frames'][0] = 0
            particle = Circle(
                [0, 0],
                ENEMY_COLOR,
                65,
                3,
                self
            )

            particle.set_goal(20, position=[0, 0], radius=0, width=3, alpha=0)
            particle.set_easings(radius='ease_in_sine', alpha='ease_in_cubic')
            scene.add_sprites(particle)

            self.delay_timers.append([25, random.choice(self.abilities).call, [scene]])

        self.ai.update(scene, dt, scene.player)
        self.apply_gravity(dt, .25)

        if abs(self.velocity[0]) < self.movement_info['per_frame_movespeed']:
            self.velocity[0] = 0

        self.rect.x += round(self.velocity[0] * dt)
        self.rect.y += round(self.velocity[1] * dt)

        self.set_images(scene, dt)
        super().display(scene, dt)
