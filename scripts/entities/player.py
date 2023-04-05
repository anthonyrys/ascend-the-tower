from scripts.constants import ENEMY_COLOR, HEAL_COLOR, UI_HEALTH_COLOR
from scripts.engine import Entity, Inputs

from scripts.core_systems.abilities import Dash, PrimaryAttack
from scripts.core_systems.talents import call_talents
from scripts.core_systems.combat_handler import register_heal, get_immunity_dict, get_mitigation_dict

from scripts.entities.particle_fx import Circle, Image

from scripts.services.spritesheet_loader import load_spritesheet

from scripts.ui.text_box import TextBox

import pygame
import math
import os

class Player(Entity):
    class Halo(Entity):
        def __init__(self, position, img, strata):
            img_scale = 1.5
            img = pygame.transform.scale(img, (img.get_width() * img_scale, img.get_height() * img_scale)).convert_alpha()
            img.set_colorkey((0, 0, 0, 0))

            super().__init__(position, img, None, strata)

            self.glow['active'] = True
            self.glow['size'] = 1.2
            self.glow['intensity'] = .4

            self.sin_amplifier = 1
            self.sin_frequency = .05

            self.sin_count = 0

        def display(self, player, scene, dt):
            self.rect.x = player.rect.x
            self.rect.y = player.rect.y
            
            self.rect_offset[1] = round((self.sin_amplifier * math.sin(self.sin_frequency * (self.sin_count)))) + (self.image.get_height() * .65)
            self.sin_count += 1 * dt

            super().display(scene, dt)

    def __init__(self, position, strata=None):
        super().__init__(position, pygame.Surface((24, 48)).convert_alpha(), None, strata)
        self.sprite_id = 'player'

        self.halo = self.Halo(position, pygame.image.load(os.path.join('imgs', 'entities', 'player', 'halo.png')).convert_alpha(), self.strata)

        self.rect_offset = [self.rect.width / 2, 0]

        self.timed_inputs = {}
        self.timed_input_buffer = 7

        self.healthbar = None

        self.overrides = {
            'ability': False,
            'death': False
        }

        self.state_info = {
            'dead': 0,
            'movement': None
        }

        self.default_movement_info = {
            'direction': 0,

            'friction': .75,
            'friction_frames': 0,

            'per_frame_movespeed': 3,
            'max_movespeed': 12,

            'jump_power': 24,
            'jumps': 0,
            'max_jumps': 2
        }

        self.movement_info = self.default_movement_info.copy()

        self.default_combat_info = {
            'max_health': 100,
            'health': 100,
            'regen_info': [.01, [0, 60]],

            'damage_multiplier': 1.0,
            'healing_multiplier': 1.0,

            'base_damage': 25,
            'crit_strike_chance': .15,
            'crit_strike_multiplier': 1.5,

            'knockback_resistance': 1,

            'immunities': get_immunity_dict(),
            'mitigations': get_mitigation_dict()
        }
        
        self.combat_info = self.default_combat_info.copy()

        self.img_info = {
            'imgs': {},
            'scale': 1.5,

            'frames': {},
            'frames_raw': {},
            'frame_info': {
                'idle': [50, 50],
                'run': [2, 2, 2, 2, 2],
                'jump': [1],
                'fall': [1]
            },

            'pulse_frames': 0,
            'pulse_frames_max': 0,
            'pulse_frame_color': ()
        }
        
        for name in ['idle', 'run', 'jump', 'fall']:
            self.img_info['imgs'][name] = load_spritesheet(os.path.join('imgs', 'entities', 'player', f'player-{name}.png'), self.img_info['frame_info'][name])
            self.img_info['frames'][name] = 0
            self.img_info['frames_raw'][name] = 0

        self.cooldown_timers = {
            'jump': 8
        }

        self.cooldowns = {}
        for cd in self.cooldown_timers.keys():
            self.cooldowns[cd] = 0

        self.abilities = {
            'dash': Dash(self), 
            'primary': PrimaryAttack(self),
            'ability_1': None,
            'ability_2': None,
            'ability_3': None
        }

        self.talents = []

    def on_key_down(self, scene, key):
        if scene.paused:
            return

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
        if scene.in_menu:
            return
    
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

    def on_respawn(self, scene):
        ...

    def on_death(self, scene, info):
        call_talents(scene, self, {'on_death': info})

    def on_healed(self, scene, info):
        if info['type'] == 'passive': 
            return
        
        color = HEAL_COLOR
        if 'color' in info:
            color = info['color']
        
        img = TextBox((0, 0), info['amount'], color=color, size=1.0).image.copy()
        particle = Image((125, 50), img, 5, 255)
        particle.set_goal(
            50, 
            position=(125, 100),
            alpha=0,
            dimensions=(img.get_width(), img.get_height())
        )
        particle.uses_ui_surface = True
        
        scene.add_sprites(particle)

    def on_damaged(self, scene, info):
        sprite = info['primary']

        scene.set_dt_multiplier(.2, 5)
        self.combat_info['immunities'][info['type']] = 30

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
        self.img_info['pulse_frames'] = 30
        self.img_info['pulse_frames_max'] = 30
        self.img_info['pulse_frame_color'] = ENEMY_COLOR

        img = TextBox((0, 0), info['amount'], color=UI_HEALTH_COLOR, size=1.0).image.copy()
        particle = Image((50, 50), img, 5, 255)
        particle.set_goal(
            50, 
            position=(50, 100),
            alpha=0,
            dimensions=(img.get_width(), img.get_height())
        )
        particle.uses_ui_surface = True

        call_talents(scene, self, {'on_damaged': info})

        scene.add_sprites(particle)

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

        if not [c for c in self.collisions if c.secondary_sprite_id == 'ramp']:
            self.apply_collision_x_default([s for s in scene.sprites if s.secondary_sprite_id == 'block'])

    def apply_collision_y(self, scene, dt):
        pressed = Inputs.pressed

        self.collide_points['top'] = False
        self.collide_points['bottom'] = False

        if 'bottom' in self.apply_collision_y_default([s for s in scene.sprites if s.secondary_sprite_id == 'block']):
            if self.movement_info['jumps'] != self.movement_info['max_jumps']:
                self.movement_info['jumps'] = self.movement_info['max_jumps']

        if 'bottom' in self.apply_collision_y_default([s for s in scene.sprites if s.secondary_sprite_id == 'floor']):
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

        ramps = [s for s in scene.sprites if s.secondary_sprite_id == 'ramp']
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
        
        afterimage_plr = Image(
            self.center_position,
            self.image.copy(), self.strata - 1, 50
        )
        
        afterimage_plr.set_goal(5, alpha=0, dimensions=self.image.get_size())

        afterimage_halo = None
        if halo:
            afterimage_halo = Image(
                (self.rect.centerx - self.halo.rect_offset[0], self.rect.centery - self.halo.rect_offset[1] * 1.8),
                self.halo.image.copy(), self.strata - 1, 50
            )

            afterimage_halo.set_goal(5, alpha=0, dimensions=self.halo.image.get_size())

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

        if dt != 0:
            mouse_pos_x = scene.mouse.rect.centerx + scene.camera_offset[0]

            if mouse_pos_x > self.rect.centerx:
                self.movement_info['direction'] = 1

            elif mouse_pos_x < self.rect.centerx:
                self.movement_info['direction'] = -1

        if self.state_info['movement'] == 'run':
            et = 1 if abs(self.velocity[0] / self.movement_info['max_movespeed']) > 1 else abs(self.velocity[0] / self.movement_info['max_movespeed'])

        if len(self.img_info['imgs'][self.state_info['movement']]) <= self.img_info['frames'][self.state_info['movement']]:
            self.img_info['frames'][self.state_info['movement']] = 0
            self.img_info['frames_raw'][self.state_info['movement']] = 0

        img = self.img_info['imgs'][self.state_info['movement']][self.img_info['frames'][self.state_info['movement']]]

        self.img_info['frames_raw'][self.state_info['movement']]  += (1 * et) * dt
        self.img_info['frames'][self.state_info['movement']] = round(self.img_info['frames_raw'][self.state_info['movement']])

        for frame in self.img_info['frames']:
            if self.state_info['movement'] == frame:
                continue

            if self.img_info['frames'][frame] == 0:
                continue

            self.img_info['frames'][frame] = 0
            self.img_info['frames_raw'][frame] = 0

        self.image = pygame.transform.scale(img, (img.get_width() * self.img_info['scale'], img.get_height() * self.img_info['scale'])).convert_alpha()
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
            if self.movement_info['friction'] != self.default_movement_info['friction']:
                self.movement_info['friction'] = self.default_movement_info['friction']
                self.movement_info['friction_frames'] = 0

        self.combat_info['regen_info'][1][0] += 1 * dt
        if self.combat_info['regen_info'][1][0] >= self.combat_info['regen_info'][1][1]:
            self.combat_info['regen_info'][1][0] = 0

            if self.combat_info['health'] < self.combat_info['max_health']:
                register_heal(
                    scene,
                    self, 
                    {'type': 'passive', 'amount': self.combat_info['max_health'] * self.combat_info['regen_info'][0]}
                )

        if self.combat_info['health'] > self.combat_info['max_health']:
            self.combat_info['health'] = self.combat_info['max_health']

        for immunity in self.combat_info['immunities'].keys():
            if '&' in immunity or self.combat_info['immunities'][immunity] == 0:
                continue

            if self.combat_info['immunities'][immunity] < 0:
                self.combat_info['immunities'][immunity] = 0
                continue

            self.combat_info['immunities'][immunity] -= 1 * dt

        del_list = []
        for mitigation in self.combat_info['mitigations']:
            if '&' in mitigation:
                continue
        
            for name, values in self.combat_info['mitigations'][mitigation].items():
                if values[1] <= 0:
                    del_list.append([mitigation, name])
                    continue

                self.combat_info['mitigations'][mitigation][name][1] -= 1 * dt

        for item in del_list:
            del self.combat_info['mitigations'][item[0]][item[1]]

        for ability in [s for s in self.abilities.values() if s is not None]:
            ability.update(scene, dt)  

        self.overrides['ability'] = False
        for ability in [s for s in self.abilities.values() if s is not None]:
            if ability is None:
                continue
    
            if ability.overrides:
                self.overrides['ability'] = True

        if self.overrides['ability']:
            for talent in self.talents:
                talent.update(scene, dt)  

            self.combat_info['crit_strike_chance'] = round(self.combat_info['crit_strike_chance'], 2)

            super().display(scene, dt)
            return     
               
        if not scene.paused:
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
            
        self.halo.display(self, scene, dt)
        self.set_images(scene, dt)
            
        for talent in self.talents:
            talent.update(scene, dt)  

        self.combat_info['crit_strike_chance'] = round(self.combat_info['crit_strike_chance'], 2)

        super().display(scene, dt)
        if self.img_info['pulse_frames'] > 0:
            img = self.mask.to_surface(
                setcolor=self.img_info['pulse_frame_color'],
                unsetcolor=(0, 0, 0, 0)
            )

            img.set_alpha(255 * (self.img_info['pulse_frames'] / self.img_info['pulse_frames_max'])) 
            scene.entity_surface.blit(img, (self.rect.x - self.rect_offset[0], self.rect.y - self.rect_offset[1]))

            self.img_info['pulse_frames'] -= 1 * dt
