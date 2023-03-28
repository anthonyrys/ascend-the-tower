from src.constants import UI_HEALTH_COLOR, ENEMY_COLOR
from src.engine import Easings, Frame

import pygame
import os

class Healthbar(Frame):
    def __init__(self, player):
        img_scale = 3
        img = pygame.image.load(os.path.join('imgs', 'ui', 'hud', 'player-frame.png')).convert_alpha()
        img = pygame.transform.scale(img, (img.get_width() * img_scale, img.get_height() * img_scale))

        super().__init__((0, 0), pygame.Surface((img.get_width(), img.get_height())).convert_alpha(), None, 2)
        self.image.set_colorkey((0, 0, 0)) 

        self.player = player
        self.frame = img
        self.content_size = [img.get_width() * .825, img.get_height()]

        self.previous_health_percentage = 1
        self.tween_info = {
            'easing': getattr(Easings, 'ease_out_sine'),
            'frames': 0,
            'max_frames': 0,
            'width': None
        }

        self.backdrop = pygame.Surface((self.content_size[0], self.content_size[1])).convert_alpha()
        self.backdrop.fill((24, 24, 24))

        self.delay = pygame.Surface((self.content_size[0], self.content_size[1])).convert_alpha()
        self.delay.fill((235, 235, 235))
        self.original_delay = self.delay.copy()

        self.health = pygame.Surface((self.content_size[0], self.content_size[1])).convert_alpha()
        self.health.fill(UI_HEALTH_COLOR)
        self.original_health = self.health.copy()

    def set_tween(self, frames):
        self.tween_info['frames'] = 0
        self.tween_info['max_frames'] = frames
        self.tween_info['width'] = self.health.get_width()

    def display(self, scene, dt):
        self.image.fill((0, 0, 0, 0))

        health_percentage = self.player.combat_info['health'] / self.player.combat_info['max_health']
        if health_percentage < self.previous_health_percentage:
            self.set_tween(20)
        
        self.health = pygame.transform.scale(self.original_health, (self.original_health.get_width() * health_percentage, self.original_health.get_height()))

        if self.tween_info['frames'] < self.tween_info['max_frames']:
            abs_prog = self.tween_info['frames'] / self.tween_info['max_frames']

            tweened_width = round((self.original_delay.get_width() * health_percentage - self.tween_info['width']) * self.tween_info['easing'](abs_prog))
            self.delay = pygame.transform.scale(self.original_delay, (self.tween_info['width'] + tweened_width, self.original_delay.get_height()))

            self.tween_info['frames'] += 1 * dt

        elif self.tween_info['max_frames'] != 0:
            self.tween_info['max_frames'] = 0
            self.delay = pygame.transform.scale(self.original_delay, (self.health.get_width(), self.original_delay.get_height()))

        self.image.blit(self.backdrop, (0, 0))
        self.image.blit(self.delay, (0, 0))
        self.image.blit(self.health, (0, 0))
        self.image.blit(self.frame, (0, 0))

        super().display(scene, dt)
        self.previous_health_percentage = health_percentage



    
