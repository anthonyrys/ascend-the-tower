'''
Holds the InfoBar baseclass and subclasses.
'''

from scripts.constants import UI_HEALTH_COLOR
from scripts.engine import Easings, Frame

from scripts.ui.text_box import TextBox

import pygame
import os

class InfoBar(Frame):
    '''
    Frame element used to display information via bars.
    '''
    
    def __init__(self, position, img, dimensions, strata, alpha=None):
        super().__init__(position, img, dimensions, strata, alpha)
        self.sprite_id = 'info_bar'

class HealthBar(InfoBar):
    def __init__(self, player):
        img_scale = 3
        img = pygame.image.load(os.path.join('imgs', 'ui', 'player', 'player-frame.png')).convert_alpha()
        img = pygame.transform.scale(img, (img.get_width() * img_scale, img.get_height() * img_scale))

        super().__init__((0, 0), pygame.Surface((img.get_width(), img.get_height())).convert_alpha(), None, 2)
        self.secondary_sprite_id = 'health_bar'

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

    def on_hover_start(self, scene):
        self.hovering = True

    def on_hover_end(self, scene):
        self.hovering = False

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

        if self.hovering:
            textbox = TextBox((0, 0), f'{self.player.combat_info["health"]} / {self.player.combat_info["max_health"]}', size=.6)
            
            self.image.blit(
                textbox.image, 
                ((self.backdrop.get_width() * .5) - (textbox.image.get_width() * .5), (self.backdrop.get_height() * .5) - (textbox.image.get_height() * .85))
            )

        super().display(scene, dt)
        self.previous_health_percentage = health_percentage
    
class EnemyBar(InfoBar):
    def __init__(self, sprite):
        img_scale = 1.25
        img = pygame.image.load(os.path.join('imgs', 'ui', 'enemies', 'enemy-frame.png')).convert_alpha()
        img = pygame.transform.scale(img, (img.get_width() * img_scale, img.get_height() * img_scale))

        super().__init__((0, 0), pygame.Surface((img.get_width(), img.get_height())).convert_alpha(), None, 2)
        self.secondary_sprite_id = 'enemy_bar'

        self.uses_entity_surface = True
        self.image.set_colorkey((0, 0, 0))

        self.enemy = sprite
        self.frame = img

        self.content_size = [img.get_width(), img.get_height()]
        
        self.pulse_info = {
            'surface': pygame.Surface((self.content_size[0], self.content_size[1])).convert_alpha(),
            'original_surface': pygame.Surface((self.content_size[0], self.content_size[1])).convert_alpha(),
            'frames': 0,
            'frames_max': 0 
        }

        self.backdrop = pygame.Surface((self.content_size[0], self.content_size[1])).convert_alpha()
        self.backdrop.fill((24, 24, 24))

        self.health = pygame.Surface((self.content_size[0], self.content_size[1])).convert_alpha()
        self.health.fill(UI_HEALTH_COLOR)
        self.original_health = self.health.copy()

    def set_pulse(self, frames, color):
        self.pulse_info['surface'] = self.pulse_info['original_surface'].copy()
        self.pulse_info['surface'].fill(color)

        self.pulse_info['frames'] = frames
        self.pulse_info['frames_max'] = frames

    def display(self, scene, dt):
        self.image.fill((0, 0, 0, 0))

        health_percentage = self.enemy.combat_info['health'] / self.enemy.combat_info['max_health']
        self.health = pygame.transform.scale(self.original_health, (self.original_health.get_width() * health_percentage, self.original_health.get_height()))

        self.image.blit(self.backdrop, (0, 0))
        self.image.blit(self.health, (0, 0))

        if self.pulse_info['frames'] > 0:
            self.pulse_info['surface'].set_alpha((self.pulse_info['frames'] / self.pulse_info['frames_max']) * 255)
            self.pulse_info['surface'] = pygame.transform.scale(
                self.pulse_info['surface'], 
                (self.pulse_info['original_surface'].get_width() * health_percentage, self.pulse_info['original_surface'].get_height())
            )

            self.image.blit(self.pulse_info['surface'], (0, 0))
            self.pulse_info['frames'] -= 1 * dt

        self.image.blit(self.frame, (0, 0))

        self.rect.x = self.enemy.rect.centerx - self.image.get_width() * .5
        self.rect.y = self.enemy.rect.centery - self.image.get_height() * 3

        super().display(scene, dt)
