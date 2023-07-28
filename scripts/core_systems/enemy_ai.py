from scripts.tools import get_distance

import pygame
import random
import math

class AiTemplate:
    def __init__(self, ai_type, sprite):
        self.ai_type = ai_type
        self.sprite = sprite

    def update(self, scene, dt, target):
        ...

class HumanoidAi(AiTemplate):
    def __init__(self, sprite):
        super().__init__('humanoid', sprite)

    def update(self, scene, dt, target):
        if self.sprite.rect.x < target.rect.x:
            self.sprite.velocity[0] += (self.sprite.movement_info['per_frame_movespeed']) if self.sprite.velocity[0] < self.sprite.movement_info['max_movespeed'] else 0
        
        if self.sprite.rect.x > target.rect.x:
           self.sprite.velocity[0] -= (self.sprite.movement_info['per_frame_movespeed']) if self.sprite.velocity[0] > -(self.sprite.movement_info['max_movespeed']) else 0

        if get_distance(self.sprite, target) < 200:
            if self.sprite.rect.y - target.rect.y > self.sprite.movement_info['jump_power'] * 3:
                if self.sprite.movement_info['jumps'] > 0 and self.sprite.cooldowns['jump'] <= 0:
                    self.sprite.cooldowns['jump'] = self.sprite.cooldown_timers['jump']
                    self.sprite.movement_info['jumps'] -= 1
                    self.sprite.velocity[1] = -(self.sprite.movement_info['jump_power'])

class FlyerAi(AiTemplate):
    def __init__(self, sprite):
        super().__init__('flyer', sprite)

    def update(self, scene, dt, target):
        destination = target.center_position
        max_ms = self.sprite.movement_info['max_movespeed']
        ms = self.sprite.movement_info['per_frame_movespeed']

        if self.sprite.rect.x < destination[0]:
            self.sprite.velocity[0] += ms if self.sprite.velocity[0] < max_ms else 0
        elif self.sprite.rect.x > destination[0]:
            self.sprite.velocity[0] -= ms if self.sprite.velocity[0] > -max_ms else 0

        if self.sprite.rect.y <= destination[1]:
            self.sprite.velocity[1] += ms if self.sprite.velocity[1] < max_ms else 0
        elif self.sprite.rect.y > destination[1]:
            self.sprite.velocity[1] -= ms if self.sprite.velocity[1] > -max_ms else 0

        self.sprite.velocity[0] = round(self.sprite.velocity[0], 1)
        self.sprite.velocity[1] = round(self.sprite.velocity[1], 1)

        if self.sprite.velocity[0] > self.sprite.movement_info['max_movespeed']:
            if (abs(self.sprite.velocity[0]) - self.sprite.movement_info['max_movespeed']) < self.sprite.movement_info['friction']:
                self.sprite.velocity[0] -= (abs(self.sprite.velocity[0]) - self.sprite.movement_info['max_movespeed'])
            else:
                self.sprite.velocity[0] -= (self.sprite.movement_info['friction'])

        elif self.sprite.velocity[0] < -(self.sprite.movement_info['max_movespeed']):
            if (abs(self.sprite.velocity[0]) - self.sprite.movement_info['max_movespeed']) < self.sprite.movement_info['friction']:
                self.sprite.velocity[0] += (abs(self.sprite.velocity[0]) - self.sprite.movement_info['max_movespeed'])

            else:
                self.sprite.velocity[0] += (self.sprite.movement_info['friction'])

class FloaterAi(AiTemplate):
    def __init__(self, sprite):
        super().__init__('floater', sprite)

        self.destination_angle_range = [45, 135]
        self.destination_angle_radius = 250

        self.destination_update_frames = [90, 90]
        self.destination = None

    def update(self, scene, dt, target):
        if self.destination_update_frames[0] >= self.destination_update_frames[1]:
            a = (random.randint(self.destination_angle_range[0], self.destination_angle_range[1]) - 180) * math.pi / 180
            self.destination = [
                target.center_position[0] + self.destination_angle_radius * math.cos(a), 
                target.center_position[1] + self.destination_angle_radius * math.sin(a)
            ]

            self.destination_update_frames[0] = 0

        self.destination_update_frames[0] += 1 * dt

        max_ms = self.sprite.movement_info['max_movespeed']
        ms = self.sprite.movement_info['per_frame_movespeed']

        distance = get_distance(self.sprite.true_position, self.destination)
        if distance <= 250:
            ms *= .5
        elif distance > 500:
            ms *= 2

        if self.sprite.rect.x < self.destination[0]:
            self.sprite.velocity[0] += ms if self.sprite.velocity[0] < max_ms else 0
        elif self.sprite.rect.x > self.destination[0]:
            self.sprite.velocity[0] -= ms if self.sprite.velocity[0] > -max_ms else 0

        if self.sprite.rect.y <= self.destination[1]:
            self.sprite.velocity[1] += ms if self.sprite.velocity[1] < max_ms else 0
        elif self.sprite.rect.y > self.destination[1]:
            self.sprite.velocity[1] -= ms if self.sprite.velocity[1] > -max_ms else 0

        self.sprite.velocity[0] = round(self.sprite.velocity[0], 1)
        self.sprite.velocity[1] = round(self.sprite.velocity[1], 1)

        if self.sprite.velocity[0] > self.sprite.movement_info['max_movespeed']:
            if (abs(self.sprite.velocity[0]) - self.sprite.movement_info['max_movespeed']) < self.sprite.movement_info['friction']:
                self.sprite.velocity[0] -= (abs(self.sprite.velocity[0]) - self.sprite.movement_info['max_movespeed'])
            else:
                self.sprite.velocity[0] -= (self.sprite.movement_info['friction'])

        elif self.sprite.velocity[0] < -(self.sprite.movement_info['max_movespeed']):
            if (abs(self.sprite.velocity[0]) - self.sprite.movement_info['max_movespeed']) < self.sprite.movement_info['friction']:
                self.sprite.velocity[0] += (abs(self.sprite.velocity[0]) - self.sprite.movement_info['max_movespeed'])

            else:
                self.sprite.velocity[0] += (self.sprite.movement_info['friction'])
