from scripts import ENEMY_COLOR, CRIT_COLOR

from scripts.core_systems.abilities import Ability
from scripts.core_systems.combat_handler import get_immunity_dict, get_mitigation_dict, register_damage
from scripts.core_systems.enemy_ai import FlyerAi, FloaterAi, EncircleAi
from scripts.core_systems.status_effects import OnFire, get_debuff

from scripts.entities.physics_entity import PhysicsEntity
from scripts.visual_fx.particle import Circle, Image
from scripts.entities.projectile import ProjectileStandard

from scripts.tools.spritesheet_loader import load_spritesheet

from scripts.ui.info_bar import EnemyBar
from scripts.ui.text_box import TextBox

from scripts.tools import get_sprite_colors, check_pixel_collision, check_line_collision
from scripts.tools.bezier import presets

import pygame
import random
import math
import os

class Enemy(PhysicsEntity):
    ENEMY_FLAGS = {}

    def __init__(self, position, img, dimensions, strata, alpha):
        super().__init__(position, img, dimensions, strata, alpha)
        self.sprite_id = 'enemy'

        self.ai = None
        self.swarm = False
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
        
    def on_death(self, scene, info, true=False):
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
            cir.set_beziers(radius=presets['ease_out'])

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

            for color in get_sprite_colors(self, .35):
                radius = round(((self.image.get_width() + self.image.get_height()) / 2) * round(random.uniform(.05, .1), 2))

                cir = Circle(pos, color, radius, 0)
                cir.set_goal(
                            100, 
                            position=(pos[0] + random.randint(-350, 350), pos[1] + random.randint(-350, 350)), 
                            radius=0, 
                            width=0
                        )
                
                cir.set_gravity(5)
                cir.set_beziers(radius=presets['ease_out'])

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
            
        img = TextBox.create_text_line('default', info['amount'], size=size, color=color)

        particle = Image(self.rect.center, img, 6, 255)
        particle.set_beziers(radius=presets['ease_in'])
    
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


class Sentry(Enemy):
    def __init__(self, position, strata, level=1):
        super().__init__(position, pygame.Surface((96, 96)).convert_alpha(), None, strata, None)
        self.secondary_sprite_id = 'sentry'
        self.ai = FlyerAi(self)

        self.default_movement_info = {
            'direction': 0,

            'friction': 2,
            'friction_frames': 0,

            'per_frame_movespeed': .5,
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

            'base_damage': 30,
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

        self.img_info['imgs'] = load_spritesheet(os.path.join('resources', 'images', 'entities', 'enemies', self.secondary_sprite_id, f'{self.secondary_sprite_id}.png'))
        self.combat_info['#sentry_original_base_damage'] = self.combat_info['base_damage']

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

            average_vel = (abs(self.velocity[0]) + abs(self.velocity[1])) *.5
            average_vel = 1 if average_vel == 0 else average_vel

            self.combat_info['base_damage'] = round(self.combat_info['#sentry_original_base_damage'] * (average_vel / self.movement_info['max_movespeed']))

            self.rect.x += round(self.velocity[0] * dt)
            self.rect.y += round(self.velocity[1] * dt)

        self.set_images(scene, dt)
        self.apply_afterimages(scene, dt)
        super().display(scene, dt)

class Sentinel(Enemy):
    ENEMY_FLAGS = {'swarm': 2}

    def __init__(self, position, strata, level=1):
        super().__init__(position, pygame.Surface((32, 32)).convert_alpha(), None, strata, None)
        self.secondary_sprite_id = 'sentinel'
        self.ai = EncircleAi(self)

        self.default_movement_info = {
            'direction': 0,

            'friction': 2,
            'friction_frames': 0,

            'per_frame_movespeed': .75,
            'max_movespeed': 15,

            'jump_power': 24,
            'jumps': 0,
            'max_jumps': 1
        }

        self.movement_info = self.default_movement_info.copy()

        self.default_combat_info = {
            'max_health': 25,
            'health': 25,
            
            'health_regen_amount': 0,
            'health_regen_tick': 0,
            'health_regen_timer': 0,

            'damage_multiplier': 1.0,
            'healing_multiplier': 1.0,

            'base_damage': 10,
            'crit_strike_chance': 0,
            'crit_strike_multiplier': 0,

            'knockback_resistance': .5,
            
            'immunities': get_immunity_dict(),
            'mitigations': get_mitigation_dict()
        }

        self.combat_info = self.default_combat_info.copy()

        self.level_info = {
            'level': level,

            'max_health_scaling': .25,
            'base_damage_scaling': .1,
            'crit_strike_chance_scaling': 1.0,
            'crit_strike_multiplier_scaling': 1.0
        }

        self.set_stats()

        self.img_info = {
            'scale': 1.5,

            'damage_frames': 0,
            'damage_frames_max': 0,

            'afterimage_frames': [0, 1],
            'base_img': []
        }

        img = pygame.image.load(os.path.join('resources', 'images', 'entities', 'enemies', 'sentinel', 'sentinel.png'))
        self.img_info['base_img'] = pygame.transform.scale(img, (img.get_width() * self.img_info['scale'], img.get_height() * self.img_info['scale']))

    def set_images(self, scene, dt):
        self.image.fill((0, 0, 0, 0))

        pos_x = self.center_position[0] + self.velocity[0] * 10
        pos_y = self.center_position[1] + self.velocity[1] * 10

        angle = (180 / math.pi) * math.atan2(pos_x - self.center_position[0], pos_y - self.center_position[1])

        img = self.img_info['base_img'].copy()
        img = pygame.transform.rotate(img, angle)

        img = pygame.transform.scale(img, (img.get_width() * self.img_info['scale'], img.get_height() * self.img_info['scale']))

        self.image.blit(img, img.get_rect(center=self.image.get_rect().center))

    def apply_afterimages(self, scene, dt, visuals=True):
        average_vel = (abs(self.velocity[0]) + abs(self.velocity[1])) *.5
        average_vel = 1 if average_vel == 0 else average_vel
        
        if average_vel < 5:
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

class Elemental(Enemy):
    class Blast(Ability):
        def __init__(self, character):
            super().__init__(character)
        
            self.ability_info['damage_multiplier'] = .5
            self.ability_info['speed'] = 15
            self.ability_info['size'] = 8

            self.ability_info['signature'] = f'{self.character.secondary_sprite_id}_blast'
            self.ability_info['duration'] = 30
            self.ability_info['status_effect_multiplier'] = .5

            self.ability_info['particle_rate'] = [0, 2]

            self.ability_info['projectile_spread'] = [-15, 15]

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
            registered = register_damage(scene, self.character, sprite, {
                'type': 'magical', 
                'amount': self.character.combat_info['base_damage'] * self.ability_info['damage_multiplier']})

            if not registered:
                return

            has_debuff = get_debuff(sprite, self.ability_info['signature'])

            if has_debuff:
                has_debuff.duration = self.ability_info['duration']
                return
            
            damage = self.character.combat_info['base_damage'] * self.ability_info['status_effect_multiplier']
            debuff = OnFire(self.character, sprite, self.ability_info['signature'], damage, self.ability_info['duration'], size=5)
            sprite.debuffs.append(debuff)
        
        def projectile_display(self, projectile, scene, dt):
            self.ability_info['particle_rate'][0] += 1 * dt
            if self.ability_info['particle_rate'][0] < self.ability_info['particle_rate'][1]:
                return
            
            self.ability_info['particle_rate'][0] = 0

            pos = projectile.center_position
            pos[0] += random.randint(-20, 20)
            pos[1] += random.randint(-10, 0)

            particle = Circle(pos, self.character.img_info['tertiary_color'], 5, 0)
            particle.strata = projectile.strata - 1
            particle.set_goal(30, position=[pos[0] + random.randint(-25, 25), pos[1] + random.randint(-25, 0)], radius=0, width=0)

            particle.glow['active'] = True
            particle.glow['size'] = 2
            particle.glow['intensity'] = .25

            scene.add_sprites(particle)

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
                'collisions': ['player'],
                'collision_function': {
                    'player': self.collision_player,
                    'default': self.collision_default
                }
            }

            projectiles = []

            proj = ProjectileStandard(
                self.character.center_position, self.character.img_info['color'], self.ability_info['size'], self.character.strata + 1,
                proj_info,
                velocity=vel,
                duration=90,
                settings={'display': self.projectile_display}
            )

            proj.glow['active'] = True
            proj.glow['size'] = 1.5
            proj.glow['intensity'] = .25

            projectiles.append(proj)

            for angle in self.ability_info['projectile_spread']:
                proj = ProjectileStandard(
                    self.character.center_position, self.character.img_info['color'], self.ability_info['size'], self.character.strata + 1,
                    proj_info,
                    velocity=list(pygame.Vector2(*vel).rotate(angle)),
                    duration=90,
                    settings={'display': self.projectile_display}
                )

                proj.glow['active'] = True
                proj.glow['size'] = 1.5
                proj.glow['intensity'] = .25

                projectiles.append(proj)

            particles = []
            for _ in range(5):
                cir = Circle(self.character.center_position, self.character.img_info['secondary_color'], 6, 0)
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
            scene.add_sprites(projectiles)

    def __init__(self, position, strata, level=1):
        super().__init__(position, pygame.Surface((40, 40)).convert_alpha(), None, strata, None)
        self.secondary_sprite_id = 'elemental'
        self.ai = FloaterAi(self)
        
        self.glow['active'] = True
        self.glow['intensity'] = .25
        self.glow['size'] = 1.15

        self.default_movement_info = {
            'direction': 0,

            'friction': 2,
            'friction_frames': 0,

            'per_frame_movespeed': .5,
            'max_movespeed': 10,

            'jump_power': 1,
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

            'knockback_resistance': .5,
            
            'immunities': get_immunity_dict(),
            'mitigations': get_mitigation_dict()
        }

        self.combat_info = self.default_combat_info.copy()

        self.level_info = {
            'level': level,

            'max_health_scaling': .4,
            'base_damage_scaling': .1,
            'crit_strike_chance_scaling': 1.0,
            'crit_strike_multiplier_scaling': 1.0
        }

        self.set_stats()

        self.img_info = {
            'damage_frames': 0,
            'damage_frames_max': 0,

            'color': (255, 144, 98),
            'secondary_color': (255, 158, 107),
            'tertiary_color': (255, 172, 107),

            'particle_rate': [0, 4],

            'imgs': [],
            'img_frames': 0
        }

        self.img_info['imgs'] = load_spritesheet(os.path.join('resources', 'images', 'entities', 'enemies', self.secondary_sprite_id, f'{self.secondary_sprite_id}.png'), scale=2)

        self.ability_info = {
            'activation_frames': [0, 75],
            'activation_cancel': False
        }

        self.abilities.append(self.Blast(self))

    def on_damaged(self, scene, info):
        super().on_damaged(scene, info)

        self.ability_info['activation_frames'][0] = random.randint(0, 5)
        self.ability_info['activation_cancel'] = True

    def set_images(self, scene, dt):
        self.img_info['img_frames'] += (1 * .3) * dt
        if self.img_info['img_frames'] >= len(self.img_info['imgs']) - 1:
            self.img_info['img_frames'] = 0

        self.image.fill((0, 0, 0, 0))
        self.image.blit(
            self.img_info['imgs'][round(self.img_info['img_frames'])], 
            self.img_info['imgs'][round(self.img_info['img_frames'])].get_rect(center=self.image.get_rect().center)
        )

        if self.img_info['damage_frames'] <= 0:
            direction = [
                scene.player.center_position[0] - self.center_position[0],
                scene.player.center_position[1] - self.center_position[1]
            ]
            multiplier = 6 / math.sqrt(math.pow(direction[0], 2) + math.pow(direction[1], 2))
            vel = [direction[0] * multiplier, direction[1] * multiplier]

            position = [self.image.get_rect().centerx + vel[0], self.image.get_rect().centery + vel[1] + 3]
            pygame.draw.circle(self.image, (0, 0, 0, 0), [position[0] + 6, position[1]], 4)
            pygame.draw.circle(self.image, (0, 0, 0, 0), [position[0] - 6, position[1]], 4)

        self.img_info['particle_rate'][0] += 1 * dt
        if self.img_info['particle_rate'][0] < self.img_info['particle_rate'][1]:
            return
        
        self.img_info['particle_rate'][0] = 0

        pos = self.center_position
        pos[0] += random.randint(-20, 20)
        pos[1] += random.randint(-20, -10)

        particle = Circle(pos, get_sprite_colors(self)[0], 7, 0)
        particle.strata = self.strata - 1
        particle.set_goal(60, position=[pos[0] + random.randint(-50, 50), pos[1] + random.randint(-75, 0)], radius=0, width=0)

        particle.glow['active'] = True
        particle.glow['size'] = 2
        particle.glow['intensity'] = .25

        scene.add_sprites(particle)

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
            self.delay_timers.append([30, random.choice(self.abilities).call, [scene]])

        self.ai.update(scene, dt, scene.player)

        if abs(self.velocity[0]) < self.movement_info['per_frame_movespeed']:
            self.velocity[0] = 0

        self.rect.x += round(self.velocity[0] * dt)
        self.rect.y += round(self.velocity[1] * dt)

        self.set_images(scene, dt)
        super().display(scene, dt)


ENEMIES = {
    1: [Sentinel, Sentry, Elemental]
}
