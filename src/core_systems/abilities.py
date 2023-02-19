from src.constants import PRIMARY_COLOR
from src.engine import SpriteMethods
from src.entities.particle_fx import Particle, Circle, Image

from src.core_systems.combat_handler import CombatMethods

from src.entities.tiles import Tile, Platform
from src.entities.enemy import Enemy

import pygame
import random
import os

class Ability:
    def __init__(self, character):
        self.character = character
        self.overrides = False

        self.ability_id = None

        self.ability_info = {
            'cooldown_timer': 0,
            'cooldown': 0
        }

        self.keybind_info = {
            'double_tap': False,
            'keybinds': []
        }

    def call(self, scene, keybind=None):
        print(f'{self.ability_id}::call()')
    
    def update(self, scene, dt):
        if self.ability_info['cooldown'] > 0:
            self.ability_info['cooldown'] -= 1 * dt

class Dash(Ability):
    def __init__(self, character):
        super().__init__(character)
        self.ability_id = 'base_a0'

        self.ability_info['cooldown_timer'] = 45
        self.ability_info['velocity'] = character.movement_info['max_movespeed'] * 3

        self.keybind_info['double_tap'] = True
        self.keybind_info['keybinds'] = ['left', 'right']

    def call(self, scene, keybind=None):
        if self.ability_info['cooldown'] > 0:
            return
        
        self.ability_info['cooldown'] = self.ability_info['cooldown_timer']

        if keybind == 'left':
            self.character.velocity[0] = -self.ability_info['velocity']
        elif keybind == 'right':
            self.character.velocity[0] = self.ability_info['velocity']

class Teleport(Ability):
    def __init__(self, character):
        super().__init__(character)
        self.ability_id = 'base_a1'

        self.img_scale = 1.5
        self.image = pygame.image.load(os.path.join('imgs', 'player', 'teleport.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.img_scale, self.image.get_height() * self.img_scale)).convert_alpha()

        self.state = 'inactive'
        self.collision_state = None

        self.velocity = []
        self.destination = []

        self.ability_info['cooldown_timer'] = 60
        self.ability_info['speed'] = 60
        self.ability_info['gravity_frames'] = 20
        self.ability_info['hit_immunity'] = 30

        self.ability_info['damage'] = 25

        self.keybind_info['keybinds'] = [1]

    def call(self, scene, keybind=None): 
        if self.ability_info['cooldown'] > 0:
            return

        if (SpriteMethods.get_distance(self.character.center_position, scene.mouse.entity_pos) < 75):
            return

        self.ability_info['cooldown'] = self.ability_info['cooldown_timer']

        self.overrides = True
        self.state = 'active'

        self.destination = [scene.mouse.entity_pos[0], scene.mouse.entity_pos[1]]

        distance = SpriteMethods.get_distance(self.character.center_position, self.destination)
        self.velocity = [
            (self.destination[0] - self.character.rect.centerx) / (distance / self.ability_info['speed']),
            (self.destination[1] - self.character.rect.centery) / (distance / self.ability_info['speed'])
        ]
        self.character.velocity = [self.velocity[0] * .5, self.velocity[1] * .5]

        self.destination[0] += self.velocity[0] * 2
        self.destination[1] += self.velocity[1] * 2

        self.character.image = self.image

        self.character.glow['active'] = True
        self.character.glow['size'] = 1.75
        self.character.glow['intensity'] = .15

        self.character.immunities['contact&'] = True

        particles = []
        pos = self.character.center_position
        for _ in range(5):
            cir = Circle(
                    Particle.Info(
                        65, 
                        position= (pos[0] + random.randint(-100, 100), pos[1] + random.randint(-100, 100)), 
                        radius=0, 
                        width=0
                    ),
                    pos, PRIMARY_COLOR, 6, 0
                )
            
            cir.glow['active'] = True
            cir.glow['size'] = 1.2
            cir.glow['intensity'] = .25

            particles.append(cir)

        scene.add_sprites(particles)    
        scene.camera.set_camera_tween(50)

    def on_collide_tile(self, scene, dt, tile):
        self.character.velocity = [round(-self.velocity[0] * .3, 1), round(-self.velocity[1] * .3, 1)]

    def on_collide_enemy(self, scene, dt, enemy):
        particles = []
        CombatMethods.register_damage(
            scene,
            self.character, 
            enemy,
            {'type': 'contact', 'amount': self.ability_info['damage'], 'velocity': self.character.velocity}
        )

        pos = enemy.center_position
        for _ in range(8):
            cir = Circle(
                    Particle.Info(
                        125, 
                        position=(
                            pos[0] + random.randint(-250, 250), 
                            pos[1] + random.randint(-250, 250)
                        ), 
                        radius=0, 
                        width=0
                    ),
                    pos, PRIMARY_COLOR, 8, 0
                )

            cir.glow['active'] = True
            cir.glow['size'] = 1.5
            cir.glow['intensity'] = .25

            particles.append(cir)
                    
            self.character.velocity = [round(-self.velocity[0] * .5, 1), round(-abs(self.velocity[1] * .3), 1)]
            self.character.immunities['contact'] = self.ability_info['hit_immunity']

        scene.add_sprites(particles)   
    
    def update(self, scene, dt):
        if self.state != 'active':
            super().update(scene, dt)
            return
        
        collision = None
        collidables = [s for s in scene.sprites if isinstance(s, Tile) and not isinstance(s, Platform)]
        for collidable in collidables:
            if not SpriteMethods.check_pixel_collision(self.character, collidable):
                continue

            collision = collidable

        enemies = [s for s in scene.sprites if isinstance(s, Enemy)]
        for enemy in enemies:
            if not self.character.rect.colliderect(enemy.rect):
                if SpriteMethods.get_distance(self.character, enemy) > self.character.rect.height * 1.25:
                    continue
                
            collision = enemy
        
        if SpriteMethods.get_distance(self.character.center_position, self.destination) <= self.ability_info['speed'] * 2 or collision is not None:
            self.character.apply_collision_x(scene)
            self.character.apply_collision_y(scene, dt)
            self.character.set_gravity(self.ability_info['gravity_frames'], 1, 5)

            self.character.glow['active'] = False
            self.character.glow['size'] = 1.1
            self.character.glow['intensity'] = .25

            particles = []
            if isinstance(collision, Tile):
                self.on_collide_tile(scene, dt, collision)

            elif isinstance(collision, Enemy):
                scene.set_dt_multiplier(.25, 10)
                self.on_collide_enemy(scene, dt, collision)
                
            if not collision:
                pos = self.character.center_position
                for _ in range(8):
                    cir = Circle(
                            Particle.Info(
                                125, 
                                position=(
                                    pos[0] + random.randint(-150, 150) + (self.character.velocity[0] * 10), 
                                    pos[1] + random.randint(-150, 150) + (self.character.velocity[1] * 10)
                                ), 
                                radius=0, 
                                width=0
                            ),
                            pos, PRIMARY_COLOR, 8, 0
                        )

                    cir.glow['active'] = True
                    cir.glow['size'] = 1.5
                    cir.glow['intensity'] = .25

                    particles.append(cir)
        

            scene.add_sprites(particles)    

            self.velocity = []
            self.destination = []
            self.state = 'inactive'

            self.character.immunities['contact&'] = False
            self.overrides = False

            return

        self.character.rect.x += round(self.velocity[0] * dt)
        self.character.rect.y += round(self.velocity[1] * dt)
        self.character.apply_afterimages(scene, False)   

        scene.add_sprites(
            Image(
                Particle.Info(15, alpha=0),
                self.character.true_position, 
                self.character.image.copy(), self.character.strata - 1, 255
            )
        )