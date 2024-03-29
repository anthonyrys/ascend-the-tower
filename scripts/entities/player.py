from scripts import ENEMY_COLOR, HEAL_COLOR, UI_HEALTH_COLOR, SCREEN_DIMENSIONS

from scripts.core_systems.abilities import Dash, PrimaryAttack
from scripts.core_systems.talents import call_talents

from scripts.entities.entity import Entity
from scripts.entities.physics_entity import PhysicsEntity
from scripts.visual_fx.particle import Circle, Image

from scripts.tools.spritesheet_loader import load_spritesheet
from scripts.tools.sfx_manager import Sfx

from scripts.ui.text_box import TextBox
from scripts.ui.info_bar import HealthBar
from scripts.ui.hotbar import Hotbar

from scripts.tools.inputs import Inputs
from scripts.tools.bezier import presets, get_bezier_point


import pygame
import random
import math
import os

class Player(PhysicsEntity):
    class Halo(Entity):
        def __init__(self, strata):
            img = pygame.image.load(os.path.join('resources', 'images', 'entities', 'player', 'halo.png')).convert_alpha()
            img_scale = 1.5
            img = pygame.transform.scale(img, (img.get_width() * img_scale, img.get_height() * img_scale)).convert_alpha()
            img.set_colorkey((0, 0, 0))

            super().__init__((0, 0), img, None, strata)

            self.glow['active'] = True
            self.glow['size'] = 1.2
            self.glow['intensity'] = .5

            self.sin_amplifier = 1
            self.sin_frequency = .05

            self.sin_count = 0

        def display(self, player, scene, dt):
            self.rect.centerx = player.rect.centerx
            self.rect.centery = player.rect.top - 5 - round((self.sin_amplifier * math.sin(self.sin_frequency * (self.sin_count))))
            
            self.sin_count += 1 * dt

            primary_ability = player.abilities['primary']
            if primary_ability.ability_info['cooldown'] > 0:
                self.glow['active'] = False
                self.image.set_alpha(55)

            elif primary_ability.ability_info['cooldown'] <= 0 and primary_ability.charges and not self.glow['active']:
                self.glow['active'] = True
                self.set_alpha_bezier(255, 5, [*presets['rest'], 0])

            super().display(scene, dt)

    def __init__(self, position, strata=None):
        super().__init__(position, pygame.Surface((24, 48)).convert_alpha(), None, strata)
        self.sprite_id = 'player'

        self.visuals.append(self.Halo(self.strata))

        self.rect_offset = [self.rect.width / 2, 0]

        self.timed_inputs = {}
        self.timed_input_buffer = 7

        self.overrides = {
            'inactive': False,
            'inactive-all': False,
            
            'ability': None,
            'ability-passive': None,

            'death': False
        }

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
            'pulse_frame_color': (),
            'pulse_frame_bezier': [*presets['rest'], 0],

            'afterimage_frames': [0, 1]
        }
        
        for name in ['idle', 'run', 'jump', 'fall']:
            self.img_info['imgs'][name] = load_spritesheet(os.path.join('resources', 'images', 'entities', 'player', f'player-{name}.png'), self.img_info['frame_info'][name])
            self.img_info['frames'][name] = 0
            self.img_info['frames_raw'][name] = 0

        self.abilities = {
            'dash': Dash(self), 
            'primary': PrimaryAttack(self),
            'ability_1': None,
            'ability_2': None
        }

        self.talents = []
        self.talent_info = {}

    def get_ui_elements(self):
        ui_elements = []

        ui_elements.append(HealthBar(self))
        ui_elements.append(Hotbar(self, (SCREEN_DIMENSIONS[0] * .5, SCREEN_DIMENSIONS[1] - 70), 3))

        return ui_elements

    def get_ability(self, ability_id):
        for ability in self.abilities.values():
            if not ability:
                continue
            
            if ability.ABILITY_ID == ability_id:
                return ability
        
        return None

    def on_key_down(self, scene, key):
        if scene.paused:
            return

        for action, keybinds in Inputs.KEYBINDS.items():
            if key not in keybinds:
                continue

            if action in list(self.abilities.keys()):
                if self.abilities[action]:
                    self.abilities[action].call(scene, keybind=action)

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

        if self.movement_info['jumps'] <= 0:
            return
        
        self.velocity[1] = -(self.movement_info['jump_power'])

        self.movement_info['jumps'] -= 1
        self.cooldowns['jump'] = self.cooldown_timers['jump']

        pos = (
            self.rect.centerx,
            self.rect.centery + 20
        )

        circle_left = Circle(pos, (255, 255, 255), 6, 0)
        circle_left.set_goal(15, position=(pos[0] - 40, pos[1] + 10), radius=0, width=0)

        circle_right = Circle(pos, (255, 255, 255), 6, 0)
        circle_right.set_goal(15, position=(pos[0] + 40, pos[1] + 10), radius=0, width=0)

        scene.add_sprites(circle_left, circle_right)    

    def on_respawn(self):
        ...

    def on_death(self, scene, info, true=False):
        if not true:
            call_talents(scene, self, {'on_player_death': info})
        
        if self.get_stat('health') != 0:
            return
        
        self.combat_info['immunities']['all'] = 45
        self.overrides['inactive'] = True

        scene.set_dt_multiplier(.05, 30)
        scene.camera.set_camera_shake(0, 0)
        
        scene.scene_fx['entity_zoom']['bezier'] = presets['ease_out']
        scene.scene_fx['entity_zoom']['type'] = 'in'
        scene.scene_fx['entity_zoom']['frames'][1] = 30
        scene.scene_fx['entity_zoom']['amount'] = 1.0

        scene.delay_timers.append([30, scene.on_player_death, []])

    def on_attack(self, scene, info):
        if info:
            call_talents(scene, self, {'on_player_attack': info})

            if info['dead']:
                call_talents(scene, self, {'on_player_kill': info})

    def on_healed(self, scene, info):
        if info['type'] == 'passive': 
            return
        
        color = HEAL_COLOR

        if 'color' in info:
            color = info['color']

        img = TextBox.create_text_line('default', info['amount'], size=.75, color=color)
        particle = Image(self.rect.center, img, 6, 255)
        particle.set_beziers(radius=presets['ease_in'])
        particle.set_goal(
            45, 
            position=(self.rect.centerx + random.randint(-50, 50), particle.rect.centery + random.randint(-50, 50)),
            alpha=0,
            dimensions=(img.get_width(), img.get_height())
        )

        scene.add_sprites(particle)

    def on_damaged(self, scene, info):
        if 'minor' in info:
            img = TextBox.create_text_line('default', info['amount'], size=.75, color=UI_HEALTH_COLOR)
            particle = Image(self.rect.center, img, 6, 255)
            particle.set_beziers(radius=presets['ease_in'])
            particle.set_goal(
                45, 
                position=(self.rect.centerx + random.randint(-50, 50), particle.rect.centery + random.randint(-50, 50)),
                alpha=0,
                dimensions=(img.get_width(), img.get_height())
            )

            scene.add_sprites(particle)
            return
        
        sprite = info['primary']
        
        if self.overrides['ability']:
            self.overrides['ability'].end(scene)

        scene.set_dt_multiplier(.2, 5)
        self.combat_info['immunities'][info['type']] = 30

        self.velocity[0] = info['velocity'][0]

        if sprite.rect.centery < self.rect.centery:
            self.velocity[1] = -info['velocity'][1]
        elif sprite.rect.centery > self.rect.centery:
            self.velocity[1] = info['velocity'][1]

        self.velocity[0] *= self.combat_info['knockback_resistance']
        self.velocity[1] *= self.combat_info['knockback_resistance']

        scene.camera.set_camera_shake(20, 10)

        self.set_friction(20, .5)
        self.img_info['pulse_frames'] = 30
        self.img_info['pulse_frames_max'] = 30
        self.img_info['pulse_frame_color'] = ENEMY_COLOR
        self.img_info['pulse_frame_bezier'] = [*presets['rest'], 0]

        img = TextBox.create_text_line('default', info['amount'], size=.75, color=UI_HEALTH_COLOR)
        particle = Image(self.rect.center, img, 6, 255)
        particle.set_beziers(radius=presets['ease_in'])
        particle.set_goal(
            45, 
            position=(self.rect.centerx + random.randint(-50, 50), particle.rect.centery + random.randint(-50, 50)),
            alpha=0,
            dimensions=(img.get_width(), img.get_height())
        )

        scene.add_sprites(particle)

        call_talents(scene, self, {'on_player_damaged': info})

    def apply_movement(self, scene):
        if self.overrides['inactive'] or self.overrides['inactive-all']:
            return
        
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
        
        excludes = ['ramp']
        if self.overrides['inactive']:
            excludes.append('killbrick')

        self.apply_collision_x_default(scene, scene.get_sprites('tile', exclude=excludes))

    def apply_collision_y(self, scene, dt):
        pressed = Inputs.pressed

        self.collide_points['top'] = False
        self.collide_points['bottom'] = False

        excludes = ['ramp']
        if self.overrides['inactive']:
            excludes.append('killbrick')

        if 'bottom' in self.apply_collision_y_default(scene, scene.get_sprites('tile', exclude=excludes)):
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

        self.apply_collision_y_ramp(scene, scene.get_sprites('tile', 'ramp'))

    def apply_afterimages(self, scene, dt, visuals=True):
        if abs(self.velocity[0]) <= self.movement_info['max_movespeed'] + self.movement_info['per_frame_movespeed']:
            return
        
        self.img_info['afterimage_frames'][0] += 1 * dt
        if self.img_info['afterimage_frames'][0] < self.img_info['afterimage_frames'][1]:
            return
        
        self.img_info['afterimage_frames'][0] = 0
        
        afterimage_plr = Image(
            self.center_position,
            self.image.copy(), self.strata - 1, 50
        )
        
        afterimage_plr.set_goal(5, alpha=0, dimensions=self.image.get_size())

        afterimage_visuals = []
        if visuals:
            for visual in self.visuals:
                afterimage = Image(
                    (
                        visual.center_position[0] + self.velocity[0], 
                        visual.center_position[1] + self.velocity[1]
                    ),
                    visual.image.copy(), visual.strata - 1, 50
                )
                
                afterimage.set_goal(5, alpha=0, dimensions=visual.image.get_size())

                afterimage_visuals.append(afterimage)

        scene.add_sprites(afterimage_plr)
        scene.add_sprites(afterimage_visuals)

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

    def display(self, scene, dt):
        if self.overrides['death'] or self.overrides['inactive-all']:
            return
    
        for key in self.timed_inputs:
            self.timed_inputs[key] -= 1 * dt

            if self.timed_inputs[key] <= 0:
                self.timed_inputs[key] = 0

        self.overrides['ability'] = None
        for ability in [s for s in self.abilities.values() if s is not None]:
            if ability is None:
                continue
    
            if ability.overrides:
                self.overrides['ability'] = ability

        if self.overrides['ability']:
            for talent in self.talents:
                talent.update(scene, dt)  

            for ability in [s for s in self.abilities.values() if s is not None]:
                ability.update(scene, dt)  

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

            self.set_frame_state()

        for visual in self.visuals:
            visual.display(self, scene, dt)

        self.apply_afterimages(scene, dt)
        self.set_images(scene, dt)
            
        for talent in self.talents:
            talent.update(scene, dt)  

        for ability in [s for s in self.abilities.values() if s is not None]:
            ability.update(scene, dt)  

        self.combat_info['crit_strike_chance'] = round(self.combat_info['crit_strike_chance'], 2)

        super().display(scene, dt)
        if self.img_info['pulse_frames'] > 0:
            img = self.mask.to_surface(
                setcolor=self.img_info['pulse_frame_color'],
                unsetcolor=(0, 0, 0, 0)
            )

            img.set_alpha(255 * get_bezier_point((self.img_info['pulse_frames'] / self.img_info['pulse_frames_max']), *self.img_info['pulse_frame_bezier'])) 
            scene.entity_surface.blit(img, (self.rect.x - self.rect_offset[0], self.rect.y - self.rect_offset[1]))

            self.img_info['pulse_frames'] -= 1 * dt