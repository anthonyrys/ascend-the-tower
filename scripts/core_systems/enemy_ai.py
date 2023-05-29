'''
Holds the Ai classes that is used by the enemy classes.
'''

from scripts.engine import get_distance, check_line_collision

import pygame

class AiTemplate:
    '''
    Class that determines how the enemy should act and move.

    Variables:
        sprite: The enemy object.
        ai_type: The type of AI (changed by subclasses).

    Methods:
        update(): update the enemy object every frame.
    '''
    
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

    def update(self, scene, dt, target):
        destination = target.center_position

        max_ms = self.sprite.movement_info['max_movespeed']
        ms = self.sprite.movement_info['per_frame_movespeed']

        jp = self.sprite.movement_info['jump_power']

        if self.sprite.rect.x < destination[0]:
            self.sprite.velocity[0] += ms if self.sprite.velocity[0] < max_ms else 0
        elif self.sprite.rect.x > destination[0]:
            self.sprite.velocity[0] -= ms if self.sprite.velocity[0] > -max_ms else 0

        self.sprite.velocity[0] = round(self.sprite.velocity[0], 1)
        
        pos_a = [
            self.sprite.rect.centerx,
            self.sprite.rect.bottom + self.sprite.image.get_height()
        ]

        pos_b = [
            self.sprite.rect.centerx,
            self.sprite.rect.top - self.sprite.image.get_height()
        ]

        tiles = [s for s in scene.sprites if s.sprite_id == 'tile']

        if check_line_collision(self.sprite.rect.center, pos_a, tiles) or check_line_collision(self.sprite.rect.center, pos_b, tiles):
            self.sprite.velocity[1] -= jp if self.sprite.velocity[1] > -max_ms else 0

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
