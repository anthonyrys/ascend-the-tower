from src.constants import (
    COLORS,
    COLOR_VALUES,
    COLOR_VALUES_PRIMARY
)

from src.engine import (
    Entity,
    check_line_collision,
    get_closest_sprite
)

from src.spritesheet_loader import load_frames
from src.particle_fx import Particle, Circle, Image

from src.entities.tile import Tile
from src.entities.barrier import Barrier
from src.entities.platform import Platform
from src.entities.ramp import Ramp

import pygame
import random
import math
import os

class Player(Entity):
    def __init__(self, position, strata=None):
        super().__init__(position, pygame.Surface((32, 64)).convert_alpha(), None, strata)

        self.spawn_location = position
        self.rect_offset = (self.rect.width / 2, 0)

        self.per_frame_movespeed = 4
        self.max_movespeed = 12
        self.direction = 0
        
        self.jump_power = 24
        self.jump = 0
        self.max_jump = 2

        self.imgs = dict()
        self.frames = dict()
        self.dt_frames = dict()
        self.img_scale = 2

        for name in ['idle', 'run', 'jump', 'fall']:
            self.imgs[name] = load_frames(
            os.path.join('imgs', 'player', f'player-{name}.png'),
            os.path.join('data', 'player', f'player-{name}.json')
            )

            self.frames[name] = 0
            self.dt_frames[name] = 0

        self.keybinds = {
            'left': [pygame.K_a, pygame.K_LEFT],
            'right': [pygame.K_d, pygame.K_RIGHT],
            'down': [pygame.K_s, pygame.K_DOWN],
            'jump': [pygame.K_w, pygame.K_SPACE, pygame.K_UP],

            'ability': pygame.K_f,
            'color_forward': pygame.K_e,
            'color_backward': pygame.K_q
        }

        self.pressed = dict()
        for keybind in self.keybinds.keys():
            self.pressed[keybind] = False

        self.interact_obj = None

        self.states = {
            'dead': False,
            'interacting': False,
            'movement': None
        }

        self.ability_data = {
            0: {},
            1: {},
            2: {
                'timer': 80,
                'range': 40
            }
        }

        self.color = COLORS[0]
        self.prev_color = self.color

        self.event_timers = { 
            'color_swap': 25,
            'ability_2': self.ability_data[2]['timer'],
            'jump': 8,
            'respawn': 75
        }
        
        self.events = dict()
        for event in self.event_timers.keys():
            self.events[event] = 0

        self.render_flags = {
            'camera_shake': False
        }

    def get_keys_pressed(self):
        keys = pygame.key.get_pressed()

        for action in self.pressed.keys():
            self.pressed[action] = False

            if not isinstance(self.keybinds[action], list):
                self.pressed[action] = keys[self.keybinds[action]]
                continue

            for val in self.keybinds[action]:
                if not keys[val]:
                    continue

                self.pressed[action] = keys[val]
                break

    def on_mouse_down(self, scene):
        if scene.paused:
            return

        if self.states['dead']:
            return

        self.on_interact_start(scene)
        
    def on_mouse_up(self, scene):
        self.on_interact_end()

    def on_interact_start(self, scene):
        interactable = scene.get_selected_interactable()
        if not interactable:
            return

        if not interactable.on_interact(scene, self):
            return

        self.interact_obj = interactable
        self.states['interacting'] = True

    def on_interact_end(self):
        if not self.states['interacting']:
            return
        
        if self.interact_obj.independent:
            return

        self.states['interacting'] = False

        self.interact_obj.on_release()
        self.interact_obj = None

    def on_death(self, scene):
        self.on_interact_end()

        self.states['dead'] = True
        scene.set_dt_multiplier(5, .1)

        self.events['respawn'] = scene.frames

    def on_respawn(self, scene):
        scene.camera.set_camera_tween(55)
        self.rect.center = self.spawn_location

        self.jump = 0
        self.velocity = [0, 0]

        self.states['dead'] = False
        self.render_flags['camera_shake'] = False

        self.image.set_alpha(255)

    def on_jump(self, scene, dt):
        if not (scene.frames - self.events['jump']) >= self.event_timers['jump']:
            return

        if self.jump > 0:
            self.velocity[1] = -(self.jump_power)

            self.jump -= 1
            self.events['jump'] = scene.frames

            pos = (
                self.rect.centerx,
                self.rect.centery + 20
            )

            particles = list()
            particles.append(
                Circle(
                    Particle.Info(15, position=(pos[0] - 40, pos[1] + 10), radius=0, width=0),
                    pos, (255, 255, 255), 6, 0
                )
            )

            particles.append(
                Circle(
                    Particle.Info(15, position=(pos[0] + 40, pos[1] + 10), radius=0, width=0),
                    pos, (255, 255, 255), 6, 0
                )
            )

            scene.add_sprites(particles)    

    def on_ability(self, scene, dt):
        if self.color == COLORS[0]:
            ...

        elif self.color == COLORS[1]:
            ...

        elif self.color == COLORS[2]:       
            if not (scene.frames - self.events['ability_2']) >= self.event_timers['ability_2']:
                return

            if self.velocity == (0, 0):
                return

            start_pos = self.rect.center

            end_pos = (
                min([-self.max_movespeed, 0, self.max_movespeed], key = lambda v: abs(v - self.velocity[0])),
                min([-self.jump_power / 4, 0], key = lambda v: abs(v - self.velocity[1]))
            )

            if end_pos == (0, 0):
                return

            end_pos = (
                start_pos[0] + (end_pos[0] * self.ability_data[2]['range']),
                start_pos[1] + (end_pos[1] * self.ability_data[2]['range'])
            )

            col_sprites = [s for s in scene.sprites if isinstance(s, Tile)]
            for barrier in [s for s in scene.sprites if isinstance(s, Barrier)]:
                if self.color != barrier.color:
                    continue

                col_sprites.append(barrier)

            clipped_sprites = check_line_collision(start_pos, end_pos, col_sprites)
            if clipped_sprites:
                clip_sprite = get_closest_sprite(self, clipped_sprites)
                clipline = clip_sprite.rect.clipline(start_pos, end_pos)

                end_pos = (clipline[0][0], clipline[0][1])

            if math.sqrt((abs(end_pos[0] - start_pos[0]) **2) + (abs(end_pos[1] - start_pos[1]) **2)) < 100:
                return

            self.events['ability_2'] = scene.frames

            end_pos = list(end_pos)

            if end_pos[0] - start_pos[0] < 0:
                end_pos[0] += self.image.get_width()
            elif end_pos[0] - start_pos[0] > 0:
                end_pos[0] -= self.image.get_width()

            if end_pos[1] - start_pos[1] < 0:
                end_pos[1] += self.image.get_height()
            elif end_pos[1] - start_pos[1] > 0:
                end_pos[1] -= self.image.get_height()

            self.rect.center = end_pos
            self.velocity[1] = 0 if self.velocity[1] > 0 else self.velocity[1]

            particles = list()
            offset = (self.image.get_size()[0] / 2, self.image.get_size()[1] / 2)
            
            particles.append(
                Image(
                    Particle.Info(50, position=(start_pos[0] - offset[0], start_pos[1] - offset[1]), alpha=0),
                    (start_pos[0] - offset[0], start_pos[1] - offset[1]), self.image.copy(), None, 75
                )
            )

            for _ in range(15):            
                dest = (
                    end_pos[0] + random.randint(-200, 200) + (self.velocity[0] * 26),  
                    end_pos[1] + random.randint(-200, 200) + (self.velocity[1] * 26)
                )

                particles.append(
                    Circle(
                        Particle.Info(
                            100, position=dest, radius=0, width=0),
                        end_pos, COLOR_VALUES_PRIMARY[self.color], 10, 0
                    )
                )

            scene.add_sprites(particles)
            scene.camera.set_camera_tween(25)
            
    def apply_movement(self, scene, dt):
        if self.velocity[0] > self.max_movespeed:
            if (abs(self.velocity[0]) - self.max_movespeed) < self.per_frame_movespeed:
                self.velocity[0] -= (abs(self.velocity[0]) - self.max_movespeed)
            
            else:
                self.velocity[0] -= (self.per_frame_movespeed)

        elif self.velocity[0] < -(self.max_movespeed):
            if (abs(self.velocity[0]) - self.max_movespeed) < self.per_frame_movespeed:
                self.velocity[0] += (abs(self.velocity[0]) - self.max_movespeed)
            
            else:
                self.velocity[0] += (self.per_frame_movespeed)

        if self.pressed['right']:
            self.velocity[0] += (self.per_frame_movespeed) if self.velocity[0] < self.max_movespeed else 0
        
        if self.pressed['left']:
           self.velocity[0] -= (self.per_frame_movespeed) if self.velocity[0] > -(self.max_movespeed) else 0

        if not self.pressed['right'] and not self.pressed['left']:
            if self.velocity[0] > 0:
                self.velocity[0] -= (self.per_frame_movespeed)

            elif self.velocity[0] < 0:
                self.velocity[0] += (self.per_frame_movespeed)

        if self.pressed['jump']:
            self.on_jump(scene, dt)

    def apply_collision_x(self, scene):
        self.collide_points['right'] = False
        self.collide_points['left'] = False

        if not [c for c in self.collisions if isinstance(c, Ramp)]:
            self.apply_collision_x_default([s for s in scene.sprites if isinstance(s, Tile)])

        barriers = [s for s in scene.sprites if isinstance(s, Barrier)]
        for barrier in barriers:
            if not self.rect.colliderect(barrier.rect):
                if barrier in self.collision_ignore:
                    self.collision_ignore.remove(barrier)

                if barrier in self.collisions:
                    self.collisions.remove(barrier)
                
                continue

            if barrier in self.collision_ignore:
                continue

            if self.color != barrier.color:
                continue

            if self.rect.centerx - barrier.rect.centerx < 0:
                if self.rect.left > barrier.rect.midleft[0]:
                    if self.rect.centery - barrier.rect.centery < 0:
                        if (self.rect.top >= barrier.rect.top):
                            return True

                        else:
                            self.collision_ignore.append(barrier)

                            if barrier not in self.collisions:
                                self.collisions.append(barrier)

                            self.velocity[1] = -15

                    if self.rect.centery - barrier.rect.centery > 0:
                        if (self.rect.bottom <= barrier.rect.bottom):
                            return True

                        else:
                            self.collision_ignore.append(barrier)
                            self.velocity[1] = 15

                else:
                    if abs(self.rect.right - barrier.rect.left) > 12:
                        self.collision_ignore.append(barrier)
                        self.velocity[0] = -(self.per_frame_movespeed * 7)
                    
                    else:
                        self.rect.right = barrier.rect.left
                        self.collide_points['right'] = True

                        if barrier not in self.collisions:
                                self.collisions.append(barrier)

                        self.velocity[0] = 0

            elif self.rect.centerx - barrier.rect.centerx > 0:
                if self.rect.right < barrier.rect.midright[0]:
                    if self.rect.centery - barrier.rect.centery < 0:
                        if (self.rect.top >= barrier.rect.top):
                            return True

                        else:
                            self.collision_ignore.append(barrier)
                            self.velocity[1] = -15

                    if self.rect.centery - barrier.rect.centery > 0:
                        if (self.rect.bottom <= barrier.rect.bottom): 
                            return True

                        else:
                            self.collision_ignore.append(barrier)
                            self.velocity[1] = 15

                else:
                    if abs(self.rect.left - barrier.rect.right) > 12:
                        self.collision_ignore.append(barrier)
                        self.velocity[0] = (self.per_frame_movespeed * 7)
                    
                    else:
                        self.rect.left = barrier.rect.right
                        self.collide_points['left'] = True

                        if barrier not in self.collisions:
                            self.collisions.append(barrier)
                                
                        self.velocity[0] = 0
                    
            else:
                return True

    def apply_collision_y(self, scene, dt):
        self.collide_points['top'] = False
        self.collide_points['bottom'] = False

        if 'bottom' in self.apply_collision_y_default([s for s in scene.sprites if isinstance(s, Tile)]):
            if self.jump != self.max_jump:
                self.jump = self.max_jump
     
        platforms = [s for s in scene.sprites if isinstance(s, Platform)]
        for platform in platforms:
            if not self.rect.colliderect(platform.rect):
                if platform in self.collision_ignore:
                    self.collision_ignore.remove(platform)

                if platform in self.collisions:
                    self.collisions.remove(platform)

                continue

            if self.pressed['down'] and platform not in self.collision_ignore:
                self.collision_ignore.append(platform)
                continue

            if self.velocity[1] > 0 and self.rect.bottom <= platform.rect.top + (self.velocity[1] * dt):
                self.rect.bottom = platform.rect.top
                self.collide_points['bottom'] = True

                if platform not in self.collisions:
                    self.collisions.append(platform)

                if self.jump != self.max_jump:
                    self.jump = self.max_jump
                        
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

            if self.pressed['jump'] and ramp not in self.collision_ignore:
                self.collision_ignore.append(ramp)
                continue

            pos = ramp.get_y_value(self)
            if pos - self.rect.bottom < 4:
                self.rect.bottom = pos
                self.collide_points['bottom'] = True

                if ramp not in self.collisions:
                    self.collisions.append(ramp)

                if self.jump != self.max_jump:
                    self.jump = self.max_jump
                            
                self.velocity[1] = 0

        barriers = [s for s in scene.sprites if isinstance(s, Barrier)]
        for barrier in barriers:
            if not self.rect.colliderect(barrier.rect):
                if barrier in self.collision_ignore:
                    self.collision_ignore.remove(barrier)
                
                if barrier in self.collisions:
                    self.collisions.remove(barrier)

                continue

            if barrier in self.collision_ignore:
                continue

            if self.color != barrier.color:
                continue

            if self.velocity[1] > 0:
                self.rect.bottom = barrier.rect.top
                self.collide_points['bottom'] = True
                
                if barrier not in self.collisions:
                    self.collisions.append(barrier)

                if self.jump != self.max_jump:
                    self.jump = self.max_jump
                        
                self.velocity[1] = 0

            if self.velocity[1] < 0:
                self.rect.top = barrier.rect.bottom
                self.collide_points['top'] = True

                if barrier not in self.collisions:
                    self.collisions.append(barrier)

                self.velocity[1] = 0

    def set_color(self, scene, dt):
        frames = scene.frames

        if not (frames - self.events['color_swap']) >= self.event_timers['color_swap']:
            return

        if self.pressed['color_forward']:
            if COLORS.index(self.color) + 1 == len(COLORS):
                self.color = COLORS[0]
            else:
                self.color = COLORS[COLORS.index(self.color) + 1]

            self.events['color_swap'] = frames

        elif self.pressed['color_backward']:
            if COLORS.index(self.color) == 0:
                self.color = COLORS[-1]
            else:
                self.color = COLORS[COLORS.index(self.color) - 1]

            self.events['color_swap'] = frames

    def set_frame_state(self):
        if not self.collide_points['bottom']:
            if self.velocity[1] < 0:
                self.states['movement'] = 'jump'
                return

            else:
                self.states['movement'] = 'fall'
                return

        if self.velocity[0] > 0 or self.velocity[0] < 0:
            self.states['movement'] = 'run'
            return

        self.states['movement'] = 'idle'

    def set_image(self, scene, dt):
        img = None
        et = 1

        if self.velocity[0] > 0:
            self.direction = 1

        elif self.velocity[0] < 0:
            self.direction = -1

        if self.states['movement'] == 'run':
            et = abs(self.velocity[0] / self.max_movespeed)

        if len(self.imgs[self.states['movement']]) <= self.frames[self.states['movement']]:
            self.frames[self.states['movement']] = 0
            self.dt_frames[self.states['movement']] = 0

        img = self.imgs[self.states['movement']][self.frames[self.states['movement']]]

        self.dt_frames[self.states['movement']]  += (1 * et) * dt
        self.frames[self.states['movement']] = round(self.dt_frames[self.states['movement']])

        for frame in self.frames:
            if self.states['movement'] == frame:
                continue

            if self.frames[frame] == 0:
                continue

            self.frames[frame] = 0
            self.dt_frames[frame] = 0

        self.image = pygame.transform.scale(img, (img.get_width() * self.img_scale, img.get_height() * self.img_scale)).convert_alpha()
        self.image = pygame.transform.flip(self.image, True, False).convert_alpha() if self.direction < 0 else self.image

        if self.color != self.prev_color:
            pos = self.rect.center
            particles = list()

            particles.append(
                Circle(
                    Particle.Info(27, position=pos, radius=150, width=1),
                    pos, 
                    COLOR_VALUES_PRIMARY[self.color],
                    5,
                    15
                )
            )
            scene.add_sprites(particles)

        self.image = self.mask.to_surface(
            setcolor=COLOR_VALUES[self.color], 
            unsetcolor=(0, 0, 0, 0)
        )

        self.prev_color = self.color

    def display(self, scene, dt):
        if scene.paused:
            super().display(scene, dt)

            for event in self.events.keys():
                self.events[event] += 1 * dt

            return

        if self.states['dead']:
            if (scene.frames - self.events['respawn']) > 5 and not self.render_flags['camera_shake']:
                self.render_flags['camera_shake'] = True
                scene.camera.set_camera_shake(60)
  
                self.image.set_alpha(0)

                pos = list(self.rect.center)
                pos[0] -= self.velocity[0]
                
                particles = list()
                for _ in range(40):
                    particles.append(
                        Circle(
                            Particle.Info(150, position=(pos[0] + random.randint(-1500, 1500), pos[1] + random.randint(-1500, 1500)), radius=0, width=0),
                            pos, COLOR_VALUES_PRIMARY[self.color], 12, 0
                        )
                    )

                particles.append(
                    Circle(
                        Particle.Info(45, position=pos, radius=250, width=1),
                        pos, 
                        COLOR_VALUES_PRIMARY[self.color],
                        5,
                        15,
                    )
                )
                scene.add_sprites(particles)

            if (scene.frames - self.events['respawn']) > self.event_timers['respawn']:
                self.on_respawn(scene)

        else:
            self.get_keys_pressed()

            self.apply_gravity(dt)
            self.apply_movement(scene, dt)

            if self.pressed['ability']:
                self.on_ability(scene, dt)

            if abs(self.velocity[0]) < self.per_frame_movespeed:
                self.velocity[0] = 0

            if self.interact_obj:
                self.interact_obj.apply_interact_effect(self)

            self.rect.x += self.velocity[0] * dt
            if (self.apply_collision_x(scene)):
                self.on_death(scene)
                scene.entity_surface.blit(
                    self.image, 
                    (self.rect.x - self.rect_offset[0], self.rect.y - self.rect_offset[1], 0, 0),
                )
                
                return

            self.rect.y += self.velocity[1] * dt
            self.apply_collision_y(scene, dt)

            self.set_frame_state()
            self.set_color(scene, dt)
            self.set_image(scene, dt)

        super().display(scene, dt)
