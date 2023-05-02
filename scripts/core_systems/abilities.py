'''
File that holds Ability baseclass as well as ability subclasses.
'''

from scripts.constants import PLAYER_COLOR, SCREEN_DIMENSIONS
from scripts.engine import check_line_collision, check_pixel_collision, get_distance

from scripts.entities.particle_fx import Circle

from scripts.core_systems.talents import call_talents
from scripts.core_systems.combat_handler import register_damage

from scripts.entities.projectile import ProjectileStandard

from scripts.ui.card import Card

import pygame
import random
import inspect
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
    '''
    Ability baseclass that is meant to be inherited from.

    Variables:
        DRAW_TYPE: used to distinguish between card types.
        DRAW_SPECIAL: used to determine how a card is created.
        ABILITY_ID: the id of the ability.
        DESCRIPTION: the description of the ability; used for card creation.

        character: the entity object.
        overrides: if the entity should be overriden by the ability.

        ability_info: used for custom ability functions.
        keybind_info: information on which keybind activates the ability.

    Methods:
        fetch(): returns the card info.
        check_draw_condition(): returns whether the ability is able to be drawn.

        call(): calls the ability to activate. 
        end(): terminate the ability and return to normal entity state.
        update(): update the object every frame.
    '''

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
            
    def call(self, scene, keybind=None):
        # print(f'{self.ABILITY_ID}::call()')

        if self.ABILITY_ID is not None:
            call_talents(scene, self.character, {f'on_{self.ABILITY_ID}': self})

        call_talents(scene, self.character, {'on_ability': self})
    
    def end(self, scene):
        ...

    def update(self, scene, dt):
        if self.ability_info['cooldown'] > 0:
            self.ability_info['cooldown'] -= 1 * dt

class Dash(Ability):
    ABILITY_ID = '@dash'

    def __init__(self, character):
        super().__init__(character)

        self.ability_info['cooldown_timer'] = 30
        self.ability_info['velocity'] = character.movement_info['max_movespeed'] * 3

        self.keybind_info['double_tap'] = True
        self.keybind_info['keybinds'] = ['left', 'right']

    @staticmethod
    def check_draw_condition(player):
        return False

    def call(self, scene, keybind=None):
        if self.ability_info['cooldown'] > 0:
            return

        self.ability_info['cooldown'] = self.ability_info['cooldown_timer']
        super().call(scene, keybind)

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
        pygame.draw.circle(self.image, PLAYER_COLOR, self.image.get_rect().center, self.img_radius)
        
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.img_scale, self.image.get_height() * self.img_scale)).convert_alpha()

        self.state = 'inactive'
        self.collision_state = None

        self.velocity = []
        self.destination = []

        self.ability_info['cooldown_timer'] = 30

        self.ability_info['speed'] = 60
        self.ability_info['gravity_frames'] = 20

        self.ability_info['hit_immunity'] = 10
        self.ability_info['damage'] = character.combat_info['base_damage']
        self.ability_info['damage_type'] = 'physical'

        self.keybind_info['keybinds'] = [1]

        self.ability_info['duration'] = 0

    @staticmethod
    def check_draw_condition(player):
        return False

    def on_collide_tile(self, scene, dt, tile):
        self.character.velocity = [round(-self.velocity[0] * .3, 1), round(-self.velocity[1] * .3, 1)]

    def on_collide_enemy(self, scene, dt, enemy):
        particles = []
        info = register_damage(
            scene,
            self.character, 
            enemy,
            {'type': self.ability_info['damage_type'], 'amount': self.ability_info['damage'], 'velocity': self.character.velocity}
        )
        
        self.character.on_attack(scene, info)

        pos = enemy.center_position
        for _ in range(8):
            cir = Circle(pos, PLAYER_COLOR, 8, 0)
            cir.set_goal(
                        75, 
                        position=(pos[0] + random.randint(-250, 250), pos[1] + random.randint(-250, 250)), 
                        radius=0, 
                        width=0
                    )

            cir.glow['active'] = True
            cir.glow['size'] = 1.5
            cir.glow['intensity'] = .25

            particles.append(cir)
 
        self.character.velocity = [round(-self.velocity[0] * .5, 1), round(-abs(self.velocity[1] * .3), 1)]
        self.character.combat_info['immunities']['contact'] = self.ability_info['hit_immunity']

        scene.set_dt_multiplier(.25, 10)
        scene.add_sprites(particles)   

    def call(self, scene, keybind=None): 
        if self.ability_info['cooldown'] > 0:
            return
        
        self.destination = [scene.mouse.entity_pos[0], scene.mouse.entity_pos[1]]

        tiles = [s for s in scene.sprites if s.sprite_id == 'tile' and s.secondary_sprite_id != 'platform']

        tile_col = check_line_collision(self.character.center_position, self.destination, tiles)
        if tile_col != []:
            self.destination = list(tile_col[0][1][0])

        distance = get_distance(self.character.center_position, self.destination)

        if distance < 75:
            return
        
        self.ability_info['cooldown'] = self.ability_info['cooldown_timer']
        self.ability_info['damage'] = self.character.combat_info['base_damage']

        super().call(scene, keybind)

        self.overrides = True
        self.state = 'active'

        self.ability_info['duration'] = 0
        
        self.velocity = [
            (self.destination[0] - self.character.rect.centerx) / (distance / self.ability_info['speed']),
            (self.destination[1] - self.character.rect.centery) / (distance / self.ability_info['speed'])
        ]
        self.character.velocity = [round(self.velocity[0] * .5, 1), round(self.velocity[1] * .5, 1)]

        self.destination[0] += self.velocity[0] * 2
        self.destination[1] += self.velocity[1] * 2

        img = pygame.Surface(self.character.image.get_size()).convert_alpha()
        img.set_colorkey((0, 0, 0))
        img.blit(self.image, self.image.get_rect(center=img.get_rect().center))

        self.character.image = img

        self.character.combat_info['immunities']['contact&'] = True

        particles = []
        pos = self.character.center_position
        for _ in range(5):
            cir = Circle(pos, PLAYER_COLOR, 6, 0)
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
            cir = Circle(pos, PLAYER_COLOR, 8, 0)
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
            super().update(scene, dt)
            return
        
        collision = None
        collidables = [s for s in scene.sprites if s.sprite_id == 'tile' and s.secondary_sprite_id != 'platform']
        for collidable in collidables:
            if not check_pixel_collision(self.character, collidable):
                continue

            collision = collidable

        enemies = [s for s in scene.sprites if s.sprite_id == 'enemy']
        for enemy in enemies:
            if enemy.combat_info['immunities'][self.ability_info['damage_type'] + '&']:
                continue

            if enemy.combat_info['immunities'][self.ability_info['damage_type']] > 0:
                continue
        
            if not self.character.rect.colliderect(enemy.rect):
                if get_distance(self.character, enemy) > self.character.rect.height * 1.25:
                    continue
                
            collision = enemy
        
        if get_distance(self.character.center_position, self.destination) <= self.ability_info['speed'] * 2 or collision is not None:
            self.character.apply_collision_x(scene)
            self.character.apply_collision_y(scene, dt)
            self.character.set_gravity(self.ability_info['gravity_frames'], 1, 5)

            self.character.glow['active'] = False
            self.character.glow['size'] = 1.1
            self.character.glow['intensity'] = .25

            if not collision:
                pos = self.character.center_position
                particles = []

                for _ in range(8):
                    cir = Circle(pos, PLAYER_COLOR, 8, 0)
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

        for i in range(self.img_radius):
            cir_pos = [
                self.character.rect.centerx - (round(self.velocity[0] * dt) * (.1 * (i + 1))),
                self.character.rect.centery - (round(self.velocity[1] * dt) * (.1 * (i + 1)))
            ]

            pygame.draw.circle(scene.entity_surface, PLAYER_COLOR, cir_pos, (self.img_radius - (i + 1)))

        self.character.apply_afterimages(scene, False)

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
			
			'icon': None,
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
        img = pygame.image.load(os.path.join('imgs', 'entities', 'projectiles', 'arrow.png'))
        img.set_colorkey((0, 0, 0))

        self.ability_info['active'] = False
        self.ability_info['cooldown_timer'] = 300
        self.ability_info['damage'] = self.character.combat_info['base_damage'] * .75

        self.ability_info['image'] = pygame.transform.scale(img, (img.get_width() * IMG_SCALE, img.get_height() * IMG_SCALE))

        self.ability_info['spawn_info'] = {
            'position': [0, 0],
            'variation': [250, 50],
            'rate': [0, 3],
            'duration': [0, 105],
            'velocity': [0, 25]
        }

        self.ability_info['projectile_info'] = {
            'collision': 'pixel',
            'collision_exclude': ['particle', 'projectile'],
            'collision_function': {
                'enemy': self.collision_enemy
            },

            'duration': 45
        }

    def collision_enemy(self, scene, projectile, sprite):
        info = register_damage(scene, self.character, sprite, {'type': 'physical', 'amount': self.ability_info['damage']})
        self.character.on_attack(scene, info)

    def call(self, scene, keybind=None):
        if self.ability_info['active']:
            return

        if self.ability_info['cooldown'] > 0:
            return

        super().call(scene, keybind)
        
        self.ability_info['cooldown'] = self.ability_info['cooldown_timer']
        self.ability_info['active'] = True

        particle = Circle(
            [0, 0],
            PLAYER_COLOR,
            0,
            5,
            self.character
        )

        particle.set_goal(15, position=[0, 0], radius=60, width=1)
        scene.add_sprites(particle)

        pos = scene.mouse.entity_pos.copy()
        pos[1] -= (self.ability_info['spawn_info']['velocity'][1] * (self.ability_info['projectile_info']['duration'] * .25))

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
                velocity=self.ability_info['spawn_info']['velocity']
            )

            projectile.image.set_alpha(0)
            projectile.set_alpha_tween(15, 255)

            scene.add_sprites(projectile)
    
class EvasiveShroud(Ability):
    ABILITY_ID = 'evasive_shroud'

    DESCRIPTION = {
		'name': 'Evasive Shroud',
		'description': 'Become temporarily immune to all damage.'
	}

    @staticmethod
    def fetch():
        card_info = {
			'type': 'ability',
			
			'icon': None,
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
        self.ability_info['cooldown_timer'] = 150

        self.ability_info['frames'] = 0
        self.ability_info['frames_max'] = 45

    def call(self, scene, keybind=None):
        if self.ability_info['cooldown'] > 0:
            return
        
        self.ability_info['cooldown'] = self.ability_info['cooldown_timer']
        self.ability_info['active'] = True
        
        self.character.combat_info['immunities']['all'] = self.ability_info['frames_max']
        self.ability_info['frames'] = self.ability_info['frames_max']

        particles = []
        pos = self.character.center_position
        for _ in range(6):
            cir = Circle(pos, (255, 255, 255), 8, 0)
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
        self.character.halo.image.set_alpha(55)

        self.ability_info['frames'] -= 1 * dt

        if self.ability_info['frames'] <= 0:
            self.ability_info['active'] = False

            self.character.halo.image.set_alpha(255)
            self.character.combat_info['immunities']['all'] = False
    
            particles = []
            pos = self.character.center_position
            for _ in range(3):
                cir = Circle(pos, (255, 255, 255), 6, 0)
                cir.set_goal(
                            60, 
                            position=(pos[0] + random.randint(-50, 50), pos[1] + random.randint(-50, 50)), 
                            radius=0, 
                            width=0
                        )

                particles.append(cir)

            scene.add_sprites(particles)    
