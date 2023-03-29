from scripts.constants import PLAYER_COLOR
from scripts.engine import check_line_collision, check_pixel_collision, get_distance

from scripts.entities.particle_fx import Circle, Image

from scripts.core_systems.talents import call_talents
from scripts.core_systems.combat_handler import register_damage

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
    ABILITY_ID = None

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
            
    def call(self, scene, keybind=None):
        print(f'{self.ABILITY_ID}::call()')

        if self.ABILITY_ID is not None:
            call_talents(scene, self.character, {f'on_{self.ABILITY_ID}': self})
    
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

        self.img_scale = 1.5
        self.image = pygame.image.load(os.path.join('imgs', 'entities', 'particles', 'abilities', 'primary.png')).convert_alpha()
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

        if info:
            call_talents(scene, self.character, {'on_player_attack': info})

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

        scene.add_sprites(particles)   
        scene.set_dt_multiplier(.25, 10)

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

        self.velocity = [
            (self.destination[0] - self.character.rect.centerx) / (distance / self.ability_info['speed']),
            (self.destination[1] - self.character.rect.centery) / (distance / self.ability_info['speed'])
        ]
        self.character.velocity = [round(self.velocity[0] * .5, 1), round(self.velocity[1] * .5, 1)]

        self.destination[0] += self.velocity[0] * 2
        self.destination[1] += self.velocity[1] * 2

        self.character.image = self.image

        self.character.glow['active'] = True
        self.character.glow['size'] = 1.75
        self.character.glow['intensity'] = .15

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
                    
                    cir.set_easings(position='tooo')

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
        self.character.apply_afterimages(scene, False)   

        scene.add_sprites(
            Image(self.character.true_position, self.character.image.copy(), self.character.strata - 1, 255).set_goal(15, alpha=0)
        )