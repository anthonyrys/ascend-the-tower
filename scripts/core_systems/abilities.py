from scripts import PLAYER_COLOR

from scripts.sprite import Sprite

from scripts.core_systems.talents import call_talents, get_talent
from scripts.core_systems.combat_handler import register_damage

from scripts.entities.projectile import ProjectileStandard
from scripts.entities.particle_fx import Circle

from scripts.ui.card import Card

from scripts.tools import check_line_collision, check_pixel_collision, get_distance, get_sprite_colors
from scripts.tools.bezier import presets, get_bezier_point

import pygame
import random
import inspect
import math
import sys
import os

def get_all_abilities():
    ability_list = []
    for ability in inspect.getmembers(sys.modules[__name__], inspect.isclass):
        if not issubclass(ability[1], Ability) or ability[1].ABILITY_ID is None:
            continue

        ability_list.append(ability[1])

    return ability_list

class Ability:
    DRAW_TYPE = 'ABILITY'
    DRAW_SPECIAL = ['ability', (255, 255, 255)]

    ABILITY_ID = None
    
    DESCRIPTION = {
		'name': None,
		'description': None
	}

    @staticmethod
    def fetch():
        card_info = {
			'type': 'ability',
			
			'icon': None,
			'symbols': []
		}

        return card_info

    def __init__(self, character):
        self.character = character
        self.overrides = False

        self.ability_info = {
            'cooldown_timer': 0,
            'cooldown': 0
        }

        self.keybind_info = {
            'double_tap': False,
            'keybinds': []
        }

    @staticmethod
    def check_draw_condition(player):
        return True
            
    def call(self, scene, keybind=None, ignores_cooldown=False):
        # print(f'{self.ABILITY_ID}::call()')

        if self.ABILITY_ID is not None:
            call_talents(scene, self.character, {f'on_{self.ABILITY_ID}': self})

        call_talents(scene, self.character, {'on_ability': self})
    
    def on_primary(self, damage_done):
        ratio = damage_done / self.character.combat_info['base_damage']

        if self.ability_info['cooldown'] > 0:
            self.ability_info['cooldown'] -= 1 * ratio

        if self.ability_info['cooldown'] < 0:
            self.ability_info['cooldown'] = 0

    def end(self):
        ...

    def update(self, scene, dt):
        if self.ABILITY_ID[0] != '@':
            return
        
        if self.ability_info['cooldown'] > 0:
            self.ability_info['cooldown'] -= 1 * dt

class Dash(Ability):
    ABILITY_ID = '@dash'

    def __init__(self, character):
        super().__init__(character)

        self.ability_info['cooldown_timer'] = 30
        self.ability_info['velocity'] = character.movement_info['max_movespeed'] * 3
        self.ability_info['current_keybind'] = None

        self.keybind_info['double_tap'] = True
        self.keybind_info['keybinds'] = ['left', 'right']

    @staticmethod
    def check_draw_condition(player):
        return False

    def call(self, scene, keybind=None):
        if self.ability_info['cooldown'] > 0:
            return
        
        if any(list(self.character.overrides.values())):
            return
        
        self.ability_info['current_keybind'] = keybind
        self.ability_info['cooldown'] = self.ability_info['cooldown_timer']
        super().call(scene, keybind)

        if get_talent(self.character, 'shadowstep'):
            return

        if keybind == 'left':
            self.character.velocity[0] = -self.ability_info['velocity']
        elif keybind == 'right':
            self.character.velocity[0] = self.ability_info['velocity']

class PrimaryAttack(Ability):
    ABILITY_ID = '@primary'

    def __init__(self, character):
        super().__init__(character)

        self.img_scale = 1
        self.img_radius = 9
        self.image = pygame.Surface((self.img_radius * 2, self.img_radius * 2)).convert_alpha()
        self.image.set_colorkey((0, 0, 0))

        self.state = 'inactive'
        self.collision_state = None

        self.charges = 0
        self.max_charges = 1

        self.velocity = []
        self.start = []
        self.destination = []

        self.ability_info['color'] = PLAYER_COLOR

        self.ability_info['cooldown_timer'] = 30

        self.ability_info['speed'] = 55
        self.ability_info['gravity_frames'] = 20

        self.ability_info['hit_immunity'] = 15
        self.ability_info['damage'] = character.combat_info['base_damage']
        self.ability_info['damage_type'] = 'physical'

        self.keybind_info['keybinds'] = [1]

        self.ability_info['duration'] = 0

        self.ability_info['timer'] = [0, 20]

    @staticmethod
    def check_draw_condition(player):
        return False

    def on_collide_tile(self, scene, dt, tile):
        self.character.velocity = [round(-self.velocity[0] * .3, 1), round(-self.velocity[1] * .3, 1)]

        pos = self.character.center_position
        particles = []

        for color in get_sprite_colors(tile):
            color[3] = 255
            cir = Circle(pos, color, random.randint(5, 8), 0)
            cir.set_goal(
                        60, 
                        position=(
                            pos[0] + random.randint(-150, 150) + self.character.velocity[0] * 10, 
                            pos[1] + random.randint(-25, 25) + self.character.velocity[1] * 10
                        ), 
                        radius=0, 
                        width=0
                    )
            
            cir.set_beziers(radius=presets['ease_out'])
            cir.set_gravity(4)
            particles.append(cir)
        
        scene.add_sprites(particles)

    def on_collide_enemy(self, scene, dt, enemy):
        call_talents(scene, self.character, {f'on_{self.ABILITY_ID}_collide': self})

        particles = []
        info = register_damage(
            scene,
            self.character, 
            enemy,
            {'type': self.ability_info['damage_type'], 'amount': self.ability_info['damage'], 'velocity': self.character.velocity}
        )
        
        self.character.on_attack(scene, info)
        call_talents(scene, self.character, {f'on_{self.ABILITY_ID}_attack': info})

        for ability in [a for a in self.character.abilities.values() if a]:
            ability.on_primary(self.ability_info['damage'])

        overlap_offset = [
            self.character.center_position[0] - enemy.center_position[0],
            self.character.center_position[1] - enemy.center_position[1]
        ]

        overlap = self.character.mask.overlap_mask(enemy.mask, overlap_offset).to_surface().get_rect()
        overlap.x, overlap.y = self.character.rect.x, self.character.rect.y
        
        pos = overlap.center
        
        for _ in range(5):
            cir = Circle(pos, self.ability_info['color'], random.randint(4, 8), 0)
            cir.set_goal(
                        75, 
                        position=(pos[0] + random.randint(-250, 250), pos[1] + random.randint(-250, 250)), 
                        radius=0, 
                        width=0
                    )

            cir.glow['active'] = True
            cir.glow['size'] = 1.75
            cir.glow['intensity'] = .25

            particles.append(cir)
 
        self.character.velocity = [round(-self.velocity[0] * .5, 1), round(-abs(self.velocity[1] * .3), 1)]
        self.character.combat_info['immunities']['contact'] = self.ability_info['hit_immunity']

        scene.set_dt_multiplier(.25, 10)
        scene.add_sprites(particles)   

    def call(self, scene, keybind=None): 
        if self.ability_info['cooldown'] > 0 or self.charges <= 0:
            return
        
        if any(list(self.character.overrides.values())):
            return
        
        self.start = self.character.center_position
        self.destination = [scene.mouse.entity_pos[0], scene.mouse.entity_pos[1]]

        tiles = scene.get_sprites('tile', exclude=['platform'])
        tile_col = check_line_collision(self.start, self.destination, tiles)

        remove_tile_cols = []
        collide_sprite = Sprite((0, 0), (255, 0, 0), (5, 5), 4)
        collide_sprite.rect.center = self.character.rect.center

        for tile in tile_col:
            if tile[0].secondary_sprite_id == 'ramp' and tile[0].rect.colliderect(self.character.rect):
                if not check_pixel_collision(collide_sprite, tile[0]):
                    remove_tile_cols.append(tile)

        for tile in remove_tile_cols:
            tile_col.remove(tile)

        if tile_col != []:
            self.destination = list(tile_col[0][1][0])

        distance = get_distance(self.start, self.destination)

        if distance < 75:
            return
        
        self.ability_info['cooldown'] = self.ability_info['cooldown_timer']
        self.ability_info['damage'] = self.character.combat_info['base_damage']
        self.ability_info['timer'][0] = self.ability_info['timer'][1]

        self.charges -= 1

        super().call(scene, keybind)

        self.overrides = True
        self.state = 'active'

        self.ability_info['duration'] = 0
        
        self.image.fill((0, 0, 0))

        self.velocity = [
            (self.destination[0] - self.character.rect.centerx) / (distance / self.ability_info['speed']),
            (self.destination[1] - self.character.rect.centery) / (distance / self.ability_info['speed'])
        ]
        self.character.velocity = [round(self.velocity[0] * .5, 1), round(self.velocity[1] * .5, 1)]

        self.destination[0] += self.velocity[0] * 2
        self.destination[1] += self.velocity[1] * 2

        pygame.draw.circle(self.image, self.ability_info['color'], self.image.get_rect().center, self.img_radius)
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.img_scale, self.image.get_height() * self.img_scale)).convert_alpha()

        img = pygame.Surface(self.character.image.get_size()).convert_alpha()
        img.set_colorkey((0, 0, 0))
        img.blit(self.image, self.image.get_rect(center=img.get_rect().center))

        self.character.image = img

        self.character.combat_info['immunities']['contact&'] = True

        particles = []
        pos = self.character.center_position
        for _ in range(5):
            cir = Circle(pos, self.ability_info['color'], 6, 0)
            cir.set_goal(
                        50, 
                        position=(pos[0] + random.randint(-100, 100), pos[1] + random.randint(-100, 100)), 
                        radius=0, 
                        width=0
                    )
            
            cir.glow['active'] = True
            cir.glow['size'] = 1.2
            cir.glow['intensity'] = .25

            particles.append(cir)

        scene.add_sprites(particles)    
        scene.camera.set_camera_tween(50)

    def end(self, scene):
        self.velocity = []
        self.destination = []
        self.state = 'inactive'

        self.character.combat_info['immunities']['contact&'] = False
        self.overrides = False

        pos = self.character.center_position
        particles = []

        for _ in range(8):
            cir = Circle(pos, self.ability_info['color'], 8, 0)
            cir.set_goal(
                        125, 
                        position=(
                            pos[0] + random.randint(-150, 150) + (self.character.velocity[0] * 10), 
                            pos[1] + random.randint(-150, 150) + (self.character.velocity[1] * 10)
                        ), 
                        radius=0, 
                        width=0
                    )

            cir.glow['active'] = True
            cir.glow['size'] = 1.5
            cir.glow['intensity'] = .25

            particles.append(cir)
        
        scene.add_sprites(particles)

    def update(self, scene, dt):
        if self.state != 'active':
            if self.character.collide_points['bottom']:
                self.charges = self.max_charges
        
            super().update(scene, dt)
            return
        
        collision = None
        collidables = scene.get_sprites('tile', exclude=['platform'])
        collidables = [c for c in collidables if get_distance(self.character, c) < 100]
        
        vel_pos = [
            self.character.center_position[0] + self.character.velocity[0] * dt,
            self.character.center_position[1] + self.character.velocity[1] * dt
        ]

        for collidable in collidables:
            if collidable.secondary_sprite_id == 'ramp':
                collide_sprite = Sprite((0, 0), (255, 0, 0), (5, 5), 4)
                collide_sprite.rect.center = vel_pos

                if not check_pixel_collision(collide_sprite, collidable):
                    continue

                pos = [
                    round(self.character.center_position[0] - self.character.velocity[0] * .5),
                    round(self.character.center_position[1] - self.character.velocity[1] * .5)
                ]

                self.character.collision_ignore.append(collidable)
                self.character.rect.center = pos

                collision = collidable
                break

            line_col = check_line_collision(self.character.center_position, vel_pos, collidable)

            if line_col:
                pos = [
                    round(line_col[0][1][0][0] - self.character.velocity[0] * .5),
                    round(line_col[0][1][0][1] - self.character.velocity[1] * .5)
                ]

                self.character.collision_ignore.append(collidable)
                self.character.rect.center = pos

                collision = collidable
                break

            if not check_pixel_collision(self.character, collidable):
                continue

            collision = collidable

        enemies = scene.get_sprites('enemy')
        for enemy in enemies:
            if enemy.combat_info['immunities'][self.ability_info['damage_type'] + '&']:
                continue

            if enemy.combat_info['immunities'][self.ability_info['damage_type']] > 0:
                continue
        
            if not self.character.rect.colliderect(enemy.rect):
                if get_distance(self.character, enemy) > self.character.rect.height * 1.25:
                    continue
                
            collision = enemy
        
        self.ability_info['timer'][0] -= 1 * dt
        if get_distance(self.character.center_position, self.destination) <= self.ability_info['speed'] * 2 or collision is not None or self.ability_info['timer'][0] <= 0:
            self.character.apply_collision_x(scene)
            self.character.apply_collision_y(scene, dt)
            self.character.set_gravity(self.ability_info['gravity_frames'], 1, 5)

            self.character.glow['active'] = False
            self.character.glow['size'] = 1.1
            self.character.glow['intensity'] = .25

            if not collision:
                pos = self.character.center_position
                particles = []

                for _ in range(3):
                    cir = Circle(pos, self.ability_info['color'], 8, 0)
                    cir.set_goal(
                                125, 
                                position=(
                                    pos[0] + random.randint(-150, 150) + (self.character.velocity[0] * 10), 
                                    pos[1] + random.randint(-150, 150) + (self.character.velocity[1] * 10)
                                ), 
                                radius=0, 
                                width=0
                            )

                    cir.glow['active'] = True
                    cir.glow['size'] = 1.75
                    cir.glow['intensity'] = .25

                    particles.append(cir)
        
                scene.add_sprites(particles)

            elif collision.sprite_id == 'tile':
                self.on_collide_tile(scene, dt, collision)

            elif collision.sprite_id == 'enemy':
                self.on_collide_enemy(scene, dt, collision)

            self.velocity = []
            self.destination = []
            self.state = 'inactive'

            self.character.combat_info['immunities']['contact&'] = False
            self.overrides = False

            return

        self.character.rect.x += round(self.velocity[0] * dt)
        self.character.rect.y += round(self.velocity[1] * dt)

        if dt != 0:
            pos = self.character.center_position
            cir = Circle(pos, self.ability_info['color'], 6, 0)
            cir.set_goal(
                        75, 
                        position=(
                            pos[0] + (self.character.velocity[0] * 10), 
                            pos[1] + random.randint(-150, 150) + (self.character.velocity[1] * 10)
                        ), 
                        radius=0, 
                        width=0
                    )

            cir.glow['active'] = True
            cir.glow['size'] = 2
            cir.glow['intensity'] = .2

            scene.add_sprites(cir)

class RainOfArrows(Ability):
    ABILITY_ID = 'rain_of_arrows'

    DESCRIPTION = {
		'name': 'Rain of Arrows',
		'description': 'Call down a rain of arrows upon your enemies.'
	}

    @staticmethod
    def fetch():
        card_info = {
			'type': 'ability',
			
			'icon': 'rain-of-arrows',
			'symbols': [
                Card.SYMBOLS['type']['ability'],
				Card.SYMBOLS['action']['damage'],
				Card.SYMBOLS['ability']['physical']
            ]
		}

        return card_info

    def __init__(self, character):
        super().__init__(character)

        IMG_SCALE = 1.5
        img = pygame.image.load(os.path.join('resources', 'images', 'entities', 'projectiles', 'rain-of-arrows.png')).convert_alpha()
        img.set_colorkey((0, 0, 0))

        self.ability_info['active'] = False
        self.ability_info['cooldown_timer'] = 5
        self.ability_info['damage_percentage'] = .5
        self.ability_info['projectile_duration'] = 45

        self.ability_info['image'] = pygame.transform.scale(img, (img.get_width() * IMG_SCALE, img.get_height() * IMG_SCALE))

        self.ability_info['spawn_info'] = {
            'position': [0, 0],
            'variation': [250, 50],
            'rate': [0, 2],
            'duration': [0, 105],
            'velocity': [0, 25]
        }

        self.ability_info['projectile_info'] = {
            'collision': 'rect',
            'collisions': 'enemy',
            'collision_function': {
                'enemy': self.collision_enemy
            }
        }

    def collision_enemy(self, scene, projectile, sprite):
        damage = self.character.combat_info['base_damage'] * self.ability_info['damage_percentage']
        info = register_damage(scene, self.character, sprite, {'type': 'physical', 'amount': damage, 'velocity': None})
    
        self.character.on_attack(scene, info)

    def call(self, scene, keybind=None, ignore_cooldown=False):
        if self.ability_info['active'] and not ignore_cooldown:
            return

        if self.ability_info['cooldown'] > 0 and not ignore_cooldown:
            return

        if any(list(self.character.overrides.values())):
            return

        if not ignore_cooldown:
            self.ability_info['cooldown'] = self.ability_info['cooldown_timer']

        super().call(scene, keybind)
        
        self.ability_info['active'] = True

        particle = Circle(
            [0, 0],
            (255, 255, 255),
            0,
            5,
            self.character
        )

        particle.set_goal(15, position=[0, 0], radius=60, width=1, alpha=0)
        particle.set_beziers(alpha=[*presets['rest'], 0])

        scene.add_sprites(particle)

        pos = scene.mouse.entity_pos.copy()
        pos[1] -= (self.ability_info['spawn_info']['velocity'][1] * (self.ability_info['projectile_duration'] * .25))

        self.ability_info['spawn_info']['position'] = pos
        self.ability_info['spawn_info']['duration'][0] = 0
    
    def update(self, scene, dt):
        super().update(scene, dt)

        if not self.ability_info['active']:
            return

        self.ability_info['spawn_info']['duration'][0] += 1 * dt
        if self.ability_info['spawn_info']['duration'][0] >= self.ability_info['spawn_info']['duration'][1]: 
            self.ability_info['active'] = False
            return

        self.ability_info['spawn_info']['rate'][0] += 1 * dt
        if self.ability_info['spawn_info']['rate'][0] >= self.ability_info['spawn_info']['rate'][1]:
            self.ability_info['spawn_info']['rate'][0] = 0

            pos = self.ability_info['spawn_info']['position'].copy()
            pos[0] += random.randint(-self.ability_info['spawn_info']['variation'][0], self.ability_info['spawn_info']['variation'][0])
            pos[1] += random.randint(-self.ability_info['spawn_info']['variation'][1], self.ability_info['spawn_info']['variation'][1])

            projectile = ProjectileStandard(
                pos,
                self.ability_info['image'].copy(),
                None,
                self.character.strata + 1,
                self.ability_info['projectile_info'],
                velocity=self.ability_info['spawn_info']['velocity'],
                duration=self.ability_info['projectile_duration']
            )

            projectile.image.set_alpha(0)
            projectile.set_alpha_bezier(255, 20, presets['ease_out'])

            scene.add_sprites(projectile)
    
class IntangibleShroud(Ability):
    ABILITY_ID = 'intangible_shroud'

    DESCRIPTION = {
		'name': 'Intangible Shroud',
		'description': 'Shroud yourself in intangibility, temporarily becoming immune to all damage.'
	}

    @staticmethod
    def fetch():
        card_info = {
			'type': 'ability',
			
			'icon': 'intangible-shroud',
			'symbols': [
                Card.SYMBOLS['type']['ability'],
				Card.SYMBOLS['action']['resistance/immunity'],
				Card.SYMBOLS['ability']['special']
            ]
		}

        return card_info
    
    def __init__(self, character):
        super().__init__(character)

        self.ability_info['active'] = False
        self.ability_info['cooldown_timer'] = 2

        self.ability_info['frames'] = 0
        self.ability_info['frames_max'] = 45

    def end(self):
        super().end()

        self.ability_info['active'] = False

        for visual in self.character.visuals:
            visual.image.set_alpha(255)

        self.character.combat_info['immunities']['all'] = False

    def call(self, scene, keybind=None, ignore_cooldown=False):
        if self.ability_info['active']:
            return

        if self.ability_info['cooldown'] > 0 and not ignore_cooldown:
            return
        
        if any(list(self.character.overrides.values())):
            return

        if not ignore_cooldown:
            self.ability_info['cooldown'] = self.ability_info['cooldown_timer']

        super().call(scene, keybind)

        self.ability_info['active'] = True

        self.character.combat_info['immunities']['all'] = self.ability_info['frames_max']
        self.ability_info['frames'] = self.ability_info['frames_max']

        particles = []
        pos = self.character.center_position
        for _ in range(6):
            cir = Circle(pos, (255, 255, 255), random.randint(6, 8), 0)
            cir.set_goal(
                        75, 
                        position=(pos[0] + random.randint(-75, 75), pos[1] + random.randint(-75, 75)), 
                        radius=0, 
                        width=0
                    )

            particles.append(cir)

        scene.add_sprites(particles)    

    def update(self, scene, dt):
        super().update(scene, dt)

        if not self.ability_info['active']:
            return
        
        self.character.image.set_alpha(55)

        for visual in self.character.visuals:
            visual.image.set_alpha(55)

        self.ability_info['frames'] -= 1 * dt

        if self.ability_info['frames'] <= 0:
            self.ability_info['active'] = False

            for visual in self.character.visuals:
                visual.image.set_alpha(255)

            particles = []
            pos = self.character.center_position
            for _ in range(3):
                cir = Circle(pos, (255, 255, 255), random.randint(4, 6), 0)
                cir.set_goal(
                            60, 
                            position=(pos[0] + random.randint(-50, 50), pos[1] + random.randint(-50, 50)), 
                            radius=0, 
                            width=0
                        )

                particles.append(cir)

            scene.add_sprites(particles)    

            call_talents(scene, self.character, {f'on_{self.ABILITY_ID}_end': self})

class HolyJavelin(Ability):
    ABILITY_ID = 'holy_javelin'

    DESCRIPTION = {
		'name': 'Holy Javelin',
		'description': 'Throw a holy javelin that explodes upon impact.'
	}

    @staticmethod
    def fetch():
        card_info = {
			'type': 'ability',
			
			'icon': 'holy-javelin',
			'symbols': [
                Card.SYMBOLS['type']['ability'],
				Card.SYMBOLS['action']['damage'],
				Card.SYMBOLS['ability']['magical']
            ]
		}

        return card_info

    def __init__(self, character):
        super().__init__(character)

        IMG_SCALE = 2.5
        img = pygame.image.load(os.path.join('resources', 'images', 'entities', 'projectiles', 'holy-javelin.png')).convert_alpha()

        self.ability_info['cooldown_timer'] = 4

        self.ability_info['image'] = pygame.transform.scale(img, (img.get_width() * IMG_SCALE, img.get_height() * IMG_SCALE))

        self.ability_info['projectile_info'] = {
            'collision': 'pixel',
            'collisions': ['tile', 'enemy'],
            'collision_function': {
                'default': self.collide_default
            }
        }

        self.ability_info['speed'] = 30
        self.ability_info['damage_multiplier'] = 1.5

        self.ability_info['explosion_range'] = 275
        self.ability_info['explosion_intensity'] = 30
        
        self.ability_info['countdown'] = [0, 0]

        self.ability_info['jump_power_multiplier'] = 1.3

        self.ability_info['rotate_info'] = []

    def collide_default(self, scene, projectile, sprite):
        enemies = []

        for e in scene.get_sprites('enemy'):
            if e in enemies:
                continue

            if get_distance(projectile, e) > self.ability_info['explosion_range']:
                continue

            enemies.append(e)

        for enemy in enemies:
            direction = [
                enemy.center_position[0] - projectile.center_position[0],
                enemy.center_position[1] - projectile.center_position[1],
            ]

            multiplier = self.ability_info['explosion_intensity'] / math.sqrt(math.pow(direction[0], 2) + math.pow(direction[1], 2))
            vel = [direction[0] * multiplier, direction[1] * multiplier]

            info = register_damage(
                scene,
                self.character,
                enemy,
                {'type': 'magical', 'amount': self.character.get_stat('base_damage') * self.ability_info['damage_multiplier'], 'velocity': vel}
            )

            self.character.on_attack(scene, info)

        particles = []

        overlap_offset = [
            sprite.center_position[0] - projectile.center_position[0],
            sprite.center_position[1] - projectile.center_position[1]
        ]

        overlap = projectile.mask.overlap_mask(sprite.mask, overlap_offset).to_surface().get_rect()
        overlap.x, overlap.y = projectile.rect.x, projectile.rect.y

        pos = overlap.center

        for _ in range(8):
            cir = Circle(pos, PLAYER_COLOR, 12, 0)
            cir.set_goal(
                        round(self.ability_info['explosion_intensity'] * 3), 
                        position=(
                            pos[0] + random.randint(-self.ability_info['explosion_range'], self.ability_info['explosion_range']), 
                            pos[1] + random.randint(-self.ability_info['explosion_range'], self.ability_info['explosion_range'])
                        ), 

                        radius=0, 
                        width=0
                    )

            cir.glow['active'] = True
            cir.glow['size'] = 2
            cir.glow['intensity'] = .25

            particles.append(cir)

        scene.add_sprites(particles)

        scene.camera.set_camera_shake(round(self.ability_info['explosion_intensity'] * 1.5))
        
    def update(self, scene, dt):
        super().update(scene, dt)
        
        if self.ability_info['countdown'][1] <= 0:
            return
        
        self.ability_info['countdown'][0] -= 1 * dt
        
        direction = [
            scene.mouse.entity_pos[0] - self.character.center_position[0],
            scene.mouse.entity_pos[1] - self.character.center_position[1]
        ]
        multiplier = self.ability_info['speed'] / math.sqrt(math.pow(direction[0], 2) + math.pow(direction[1], 2))
        vel = [direction[0] * multiplier, direction[1] * multiplier]
        
        img = self.ability_info['image'].copy()
        angle = (180 / math.pi) * math.atan2(vel[0], vel[1]) - 180

        if self.ability_info['countdown'][0] > 0:
            percen = 1 - 1 * (self.ability_info['countdown'][0] / self.ability_info['countdown'][1])

            if dt != 0:
                self.ability_info['rotate_info'] = [
                    (angle + (self.character.movement_info['direction'] * (360 * (percen + .75) if (percen + .75) <= 1 else 1))),
                    [
                        self.character.center_position[0] - vel[0] * get_bezier_point(percen, [0, 0], [0, 0], [-1.5, 0], [1, 0], 0),
                        self.character.center_position[1] - vel[1] * get_bezier_point(percen, [0, 0], [0, 0], [-1.5, 0], [1, 0], 0)
                    ]
                ]

            rotate_img = pygame.transform.rotate(img, self.ability_info['rotate_info'][0])
            rotate_img.set_alpha(255 * get_bezier_point(percen, *presets['ease_out']))

            scene.entity_surface.blit(rotate_img, rotate_img.get_rect(center=self.ability_info['rotate_info'][1]))
            return
        
        self.ability_info['countdown'][1] = 0

        pos = self.character.center_position
        projectile = ProjectileStandard(
            pos,
            pygame.transform.rotate(img, angle),
            None,
            self.character.strata + 1,
            self.ability_info['projectile_info'],
            velocity=vel,
            duration=150,
            settings={
                'afterimages': [0, 1]
            }
        )

        projectile.glow['active'] = True
        projectile.glow['size'] = 1.2
        projectile.glow['intensity'] = .1

        projectile.afterimage_frames = [0, 1]

        particles = []
        for _ in range(5):
            cir = Circle(pos, PLAYER_COLOR, 6, 0)
            cir.set_goal(
                        100, 
                        position=(
                            pos[0] + random.randint(-150, 150) + (vel[0] * 10), 
                            pos[1] + random.randint(-150, 150) + (vel[1] * 10)
                        ), 
                        radius=0, 
                        width=0
                    )

            cir.glow['active'] = True
            cir.glow['size'] = 1.5
            cir.glow['intensity'] = .25

            particles.append(cir)

        scene.add_sprites(projectile)
        scene.add_sprites(particles)

        self.character.overrides['ability-passive'] = None

    def end(self):
        super().end()
        
        self.character.overrides['ability-passive'] = None

    def call(self, scene, keybind=None, ignore_cooldown=False):
        if self.ability_info['cooldown'] > 0 and not ignore_cooldown:
            return
        
        if any(list(self.character.overrides.values())):
            return

        if not ignore_cooldown:
            self.ability_info['cooldown'] = self.ability_info['cooldown_timer']

        self.ability_info['countdown'] = [20, 20]
        super().call(scene, keybind)
        
        self.character.overrides['ability-passive'] = self
        self.character.velocity[1] = -self.character.get_stat('jump_power') * self.ability_info['jump_power_multiplier']

        particle = Circle(
            [0, 0],
            PLAYER_COLOR,
            50,
            3,
            self.character
        )

        particle.set_goal(self.ability_info['countdown'][1] * 1.25, position=[0, 0], radius=0, width=3, alpha=0)
        particle.set_beziers(alpha=[*presets['rest'], 0])

        scene.set_dt_multiplier(.5, self.ability_info['countdown'][1])
        scene.add_sprites(particle)
