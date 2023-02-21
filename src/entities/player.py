from src.engine import Entity, Inputs

from src.core_systems.abilities import Dash, Teleport
from src.core_systems.combat_handler import CombatMethods

from src.entities.particle_fx import Circle, Image
from src.entities.tiles import Block, Platform, Ramp, Floor

from src.misc.spritesheet_loader import load_spritesheet

import pygame
import math
import os

class Player(Entity):
    class Halo(Entity):
        def __init__(self, position, img, strata):
            self.img_scale = 1.5

            img = pygame.transform.scale(img, (img.get_width() * self.img_scale, img.get_height() * self.img_scale)).convert_alpha()
            img.set_colorkey((0, 0, 0, 0))

            super().__init__(position, img, None, strata)

            self.glow['active'] = True
            self.glow['size'] = 1.2
            self.glow['intensity'] = .2

            self.sin_amplifier = 1
            self.sin_frequency = .05

        def display(self, player, scene, dt):
            self.rect.x = player.rect.x
            self.rect.y = player.rect.y
            
            self.rect_offset[1] = round((self.sin_amplifier * math.sin(self.sin_frequency * (scene.frame_count)))) + (self.image.get_height() * .65)

            super().display(scene, dt)

    def __init__(self, position, strata=None):
        super().__init__(position, pygame.Surface((24, 48)).convert_alpha(), None, strata)
        self.halo = self.Halo(position, pygame.image.load(os.path.join('imgs', 'player', 'halo.png')).convert_alpha(), self.strata)

        self.rect_offset = [self.rect.width / 2, 0]

        self.timed_inputs = {}
        self.timed_input_buffer = 7

        self.movement_info = {
            'direction': 0,

            'friction': .75,
            'base_friction': .75,
            'friction_frames': 0,

            'per_frame_movespeed': 3,
            'max_movespeed': 12,

            'jump_power': 24,
            'jumps': 0,
            'max_jumps': 2
        }

        self.combat_info = {
            'max_health': 100,
            'health': 55,
            'regen_info': [.01, [0, 30]],

            'knockback_resistance': 1
        }
        
        self.state_info = {
            'dead': False,
            'movement': None
        }

        self.imgs = {}
        self.damage_img = 0
        self.max_damage_img = 0
        self.img_frames = {}
        self.img_frames_raw = {}
        self.img_scale = 1.5

        self.frame_info = {
            'idle': [50, 50],
            'run': [2, 2, 2, 2, 2],
            'jump': [1],
            'fall': [1]
        }
        
        for name in ['idle', 'run', 'jump', 'fall']:
            self.imgs[name] = load_spritesheet(os.path.join('imgs', 'player', f'player-{name}.png'), self.frame_info[name])

            self.img_frames[name] = 0
            self.img_frames_raw[name] = 0

        self.cooldown_timers = {
            'jump': 8
        }

        self.cooldowns = {}
        for cd in self.cooldown_timers.keys():
            self.cooldowns[cd] = 0
        
        self.abilities = {
            'dash': Dash(self), 
            'teleport': Teleport(self),
            'ability_1': None,
            'ability_2': None,
            'ability_3': None
        }
        
        self.talents = []
        self.immunities = {}

    def on_key_down(self, scene, key):
        for action, keybinds in Inputs.KEYBINDS.items():
            if key not in keybinds:
                continue

            if self.timed_inputs.get(action):
                for ability in [a for a in self.abilities.values() if a is not None and a.keybind_info['double_tap']]:
                    for keybinds in ability.keybind_info['keybinds']:
                        if action not in keybinds:
                            continue

                        ability.call(scene, keybind=action)

            self.timed_inputs[action] = self.timed_input_buffer

    def on_mouse_down(self, scene, key):
        for ability in [s for s in self.abilities.values() if s is not None]:
            if key not in ability.keybind_info['keybinds']:
                continue

            ability.call(scene)

    def on_jump(self, scene):
        if self.cooldowns['jump'] != 0:
            return

        if self.movement_info['jumps'] > 0:
            self.velocity[1] = -(self.movement_info['jump_power'])

            self.movement_info['jumps'] -= 1
            self.cooldowns['jump'] = self.cooldown_timers['jump']

            pos =(
                self.rect.centerx,
                self.rect.centery + 20
            )

            circle_left = Circle(pos, (255, 255, 255), 6, 0)
            circle_left.set_goal(15, position=(pos[0] - 40, pos[1] + 10), radius=0, width=0)

            circle_right = Circle(pos, (255, 255, 255), 6, 0)
            circle_right.set_goal(15, position=(pos[0] + 40, pos[1] + 10), radius=0, width=0)

            scene.add_sprites(circle_left, circle_right)    

    def on_healed(self, scene, info):
        ...

    def on_damaged(self, scene, sprite, info):
        scene.set_dt_multiplier(.2, 5)
        self.immunities[info['type']] = 45

        if sprite.rect.centerx > self.rect.centerx:
            self.velocity[0] = -self.movement_info['max_movespeed'] * 2
        elif sprite.rect.centerx < self.rect.centerx:
            self.velocity[0] = self.movement_info['max_movespeed'] * 2

        if sprite.rect.centery < self.rect.centery:
            self.velocity[1] = self.movement_info['jump_power'] * .5
        elif sprite.rect.centery > self.rect.centery:
            self.velocity[1] = -self.movement_info['jump_power'] * .75

        self.velocity[0] *= self.combat_info['knockback_resistance']
        self.velocity[1] *= self.combat_info['knockback_resistance']

        scene.camera.set_camera_shake(20, 10)

        self.set_friction(20, .5)
        self.damage_img = 30
        self.max_damage_img = 30

    def apply_movement(self, scene):
        pressed = Inputs.pressed

        if self.velocity[0] > self.movement_info['max_movespeed']:
            if (abs(self.velocity[0]) - self.movement_info['max_movespeed']) < self.movement_info['friction']:
                self.velocity[0] -= (abs(self.velocity[0]) - self.movement_info['max_movespeed'])
            
            else:
                self.velocity[0] -= (self.movement_info['friction'])

        elif self.velocity[0] < -(self.movement_info['max_movespeed']):
            if (abs(self.velocity[0]) - self.movement_info['max_movespeed']) < self.movement_info['friction']:
                self.velocity[0] += (abs(self.velocity[0]) - self.movement_info['max_movespeed'])
            
            else:
                self.velocity[0] += (self.movement_info['friction'])

        if pressed['right']:
            self.velocity[0] += (self.movement_info['per_frame_movespeed']) if self.velocity[0] < self.movement_info['max_movespeed'] else 0
        
        if pressed['left']:
           self.velocity[0] -= (self.movement_info['per_frame_movespeed']) if self.velocity[0] > -(self.movement_info['max_movespeed']) else 0

        if not pressed['right'] and not pressed['left']:
            if self.velocity[0] > 0:
                self.velocity[0] -= (self.movement_info['per_frame_movespeed'])

            elif self.velocity[0] < 0:
                self.velocity[0] += (self.movement_info['per_frame_movespeed'])

        if pressed['jump']:
            self.on_jump(scene)

    def apply_collision_x(self, scene):
        self.collide_points['right'] = False
        self.collide_points['left'] = False

        if not [c for c in self.collisions if isinstance(c, Ramp)]:
            self.apply_collision_x_default([s for s in scene.sprites if isinstance(s, Block)])

    def apply_collision_y(self, scene, dt):
        pressed = Inputs.pressed

        self.collide_points['top'] = False
        self.collide_points['bottom'] = False

        if 'bottom' in self.apply_collision_y_default([s for s in scene.sprites if isinstance(s, Block)]):
            if self.movement_info['jumps'] != self.movement_info['max_jumps']:
                self.movement_info['jumps'] = self.movement_info['max_jumps']

        if 'bottom' in self.apply_collision_y_default([s for s in scene.sprites if isinstance(s, Floor)]):
            if self.movement_info['jumps'] != self.movement_info['max_jumps']:
                self.movement_info['jumps'] = self.movement_info['max_jumps']
     
        platforms = [s for s in scene.sprites if isinstance(s, Platform)]
        for platform in platforms:
            if not self.rect.colliderect(platform.rect):
                if platform in self.collision_ignore:
                    self.collision_ignore.remove(platform)

                if platform in self.collisions:
                    self.collisions.remove(platform)

                continue

            if pressed['down'] and platform not in self.collision_ignore:
                self.collision_ignore.append(platform)
                continue

            if self.velocity[1] > 0 and self.rect.bottom <= platform.rect.top + (self.velocity[1] * dt):
                self.rect.bottom = platform.rect.top
                self.collide_points['bottom'] = True

                if platform not in self.collisions:
                    self.collisions.append(platform)

                if self.movement_info['jumps'] != self.movement_info['max_jumps']:
                    self.movement_info['jumps'] = self.movement_info['max_jumps']
                        
                self.velocity[1] = 0

        ramps = [s for s in scene.sprites if isinstance(s, Ramp)]
        for ramp in ramps:
            if not self.rect.colliderect(ramp.rect):
                if ramp in self.collision_ignore:
                    self.collision_ignore.remove(ramp)
                    
                if ramp in self.collisions:
                    self.collisions.remove(ramp)
                
                continue

            if ramp in self.collision_ignore:
                continue

            if self.velocity[1] < -4 and ramp not in self.collision_ignore:
               self.collision_ignore.append(ramp) 
               continue

            pos = ramp.get_y_value(self)
            if pos - self.rect.bottom < 4:
                self.rect.bottom = pos
                self.collide_points['bottom'] = True

                if ramp not in self.collisions:
                    self.collisions.append(ramp)

                if self.movement_info['jumps'] != self.movement_info['max_jumps']:
                    self.movement_info['jumps'] = self.movement_info['max_jumps']
                            
                self.velocity[1] = 0

    def apply_afterimages(self, scene, halo=True):
        if abs(self.velocity[0]) <= self.movement_info['max_movespeed']:
            return

        x_pos = self.rect.left - self.rect.width * .5
        afterimage_plr = Image(
            (x_pos, self.rect.y), 
            self.image.copy(), self.strata - 1, 50
        )
        
        afterimage_plr.set_goal(5, alpha=0)

        afterimage_halo = None
        if halo:
            afterimage_halo = Image(
                (self.rect.left - self.halo.rect_offset[0], self.rect.y - self.halo.rect_offset[1]),
                self.halo.image.copy(), self.strata - 1, 50
            )

            afterimage_halo.set_goal(5, alpha=0)

        scene.add_sprites(afterimage_plr, afterimage_halo)

    def set_frame_state(self):
        if not self.collide_points['bottom']:
            if self.velocity[1] < 0:
                self.state_info['movement'] = 'jump'
                return

            else:
                self.state_info['movement'] = 'fall'
                return

        if self.velocity[0] > 0 or self.velocity[0] < 0:
            self.state_info['movement'] = 'run'
            return

        self.state_info['movement'] = 'idle'

    def set_images(self, scene, dt): 
        img = None
        et = 1

        mouse_pos_x = scene.mouse.rect.centerx + scene.camera_offset[0]

        if mouse_pos_x > self.rect.centerx:
            self.movement_info['direction'] = 1

        elif mouse_pos_x < self.rect.centerx:
            self.movement_info['direction'] = -1

        if self.state_info['movement'] == 'run':
            et = 1 if abs(self.velocity[0] / self.movement_info['max_movespeed']) > 1 else abs(self.velocity[0] / self.movement_info['max_movespeed'])

        if len(self.imgs[self.state_info['movement']]) <= self.img_frames[self.state_info['movement']]:
            self.img_frames[self.state_info['movement']] = 0
            self.img_frames_raw[self.state_info['movement']] = 0

        img = self.imgs[self.state_info['movement']][self.img_frames[self.state_info['movement']]]

        self.img_frames_raw[self.state_info['movement']]  += (1 * et) * dt
        self.img_frames[self.state_info['movement']] = round(self.img_frames_raw[self.state_info['movement']])

        for frame in self.img_frames:
            if self.state_info['movement'] == frame:
                continue

            if self.img_frames[frame] == 0:
                continue

            self.img_frames[frame] = 0
            self.img_frames_raw[frame] = 0

        self.image = pygame.transform.scale(img, (img.get_width() * self.img_scale, img.get_height() * self.img_scale)).convert_alpha()
        self.image = pygame.transform.flip(self.image, True, False).convert_alpha() if self.movement_info['direction'] < 0 else self.image

    def set_friction(self, frames, friction):
        self.movement_info['friction_frames'] = frames
        self.movement_info['friction'] = friction

    def display(self, scene, dt):
        for event in self.cooldowns.keys():
            if self.cooldowns[event] < 1 * dt:
                self.cooldowns[event] = 0
                continue

            self.cooldowns[event] -= 1 * dt

        for key in self.timed_inputs:
            self.timed_inputs[key] -= 1 * dt

            if self.timed_inputs[key] <= 0:
                self.timed_inputs[key] = 0

        if self.movement_info['friction_frames'] > 0:
            self.movement_info['friction_frames'] -= 1 * dt

        elif self.movement_info['friction_frames'] <= 0:
            if self.movement_info['friction'] != self.movement_info['base_friction']:
                self.movement_info['friction'] = self.movement_info['base_friction']
                self.movement_info['friction_frames'] = 0

        self.combat_info['regen_info'][1][0] += 1 * dt
        if self.combat_info['regen_info'][1][0] >= self.combat_info['regen_info'][1][1]:
            self.combat_info['regen_info'][1][0] = 0

            if self.combat_info['health'] < self.combat_info['max_health']:
                CombatMethods.register_heal(
                    scene,
                    self, 
                    {'type': 'status', 'amount': self.combat_info['max_health'] * self.combat_info['regen_info'][0]}
                )

        for immunity in self.immunities.keys():
            if self.immunities.get(immunity):
                if self.immunities[immunity] <= 0 or '&' in immunity:
                    continue

                self.immunities[immunity] -= 1 * dt

        for ability in [s for s in self.abilities.values() if s is not None]:
            ability.update(scene, dt)  

        for ability in [s for s in self.abilities.values() if s is not None]:
            if ability is None:
                continue
    
            if ability.overrides:
                super().display(scene, dt)
                return

        self.apply_gravity(dt)
        self.apply_movement(scene)
        
        if abs(self.velocity[0]) < self.movement_info['per_frame_movespeed']:
            self.velocity[0] = 0

        self.rect.x += round(self.velocity[0] * dt)
        self.apply_collision_x(scene)

        self.rect.y += round(self.velocity[1] * dt)
        self.apply_collision_y(scene, dt)

        self.apply_afterimages(scene)

        self.set_frame_state()
        self.set_images(scene, dt)

        super().display(scene, dt)
        if self.damage_img > 0:
            img = self.mask.to_surface(
                setcolor=(242, 59, 76),
                unsetcolor=(0, 0, 0, 0)
            )
            img.set_alpha(255 * (self.damage_img / self.max_damage_img)) 
            scene.entity_surface.blit(img, (self.rect.x - self.rect_offset[0], self.rect.y - self.rect_offset[1]))

            self.damage_img -= 1 * dt

        self.halo.display(self, scene, dt)