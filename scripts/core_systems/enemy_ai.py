from scripts.engine import get_distance

import pygame

class AiTemplate:
    def __init__(self, ai_type, sprite):
        self.sprite = sprite

        self.ai_type = ai_type
        self.ai_config = {
            'aggro_distance': None,
            'is_aggro': None,
            'can_collide': None
        }

    def update(self, scene, dt, target):
        ...

class Flyer(AiTemplate):
    def __init__(self, sprite):
        super().__init__('flyer', sprite)

        self.ai_config['aggro_distance'] =  960
        self.ai_config['is_aggro'] = False
        self.ai_config['can_collide'] = False

    def update(self, scene, dt, target):
        distance = get_distance(self.sprite, target)
        if distance <= self.ai_config['aggro_distance'] and not self.ai_config['is_aggro']:
            self.ai_config['is_aggro'] = True
            
        elif distance > self.ai_config['aggro_distance'] and self.ai_config['is_aggro']:
            self.ai_config['is_aggro'] = False

        destination = target.center_position
        max_ms = self.sprite.movement_info['max_movespeed']
        ms = self.sprite.movement_info['per_frame_movespeed']

        if not self.ai_config['is_aggro']:
            if self.sprite.velocity[0] != 0:
                if self.sprite.velocity[0] > 0:
                    self.sprite.velocity[0] -= ms

                elif self.sprite.velocity[0] < 0:
                    self.sprite.velocity[0] += ms
                
                if abs(self.sprite.velocity[0]) <= max_ms:
                    self.sprite.velocity[0] = 0

            if self.sprite.velocity[1] != 0:
                if self.sprite.velocity[1] > 0:
                    self.sprite.velocity[1] -= ms

                elif self.sprite.velocity[1] < 0:
                    self.sprite.velocity[1] += ms

                if abs(self.sprite.velocity[1]) <= max_ms:
                    self.sprite.velocity[1] = 0

            return

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

        self.sprite.rect.x += round(self.sprite.velocity[0] * dt)
        self.sprite.rect.y += round(self.sprite.velocity[1] * dt)
