'''
Holds the Interactable baseclass and subclasses.
'''

from scripts.constants import PLAYER_COLOR
from scripts.engine import Entity, create_outline_full

from scripts.entities.particle_fx import Circle

import pygame
import random
import math
import os

class Interactable(Entity):
    '''
    Entity class that the player can interact with.

    Variables:
        interactable: whether the object can be interacted with.
        on_interact: function that is called when the player interacts.

        selected: whether the player has the object selected.
        selected_text: the text that will be displayed upon selecting.
        selected_color: the color of selected_text.
    '''
    
    def __init__(self, position, img, dimensions, strata, alpha, on_interact=None):
        super().__init__(position, img, dimensions, strata, alpha)
        self.sprite_id = 'interactable'

        self.interactable = True
        if not hasattr(self, 'on_interact'):
            self.on_interact = on_interact

        self.selected = False
        self.selected_text = 'null'
        self.selected_color = (255, 255, 255)

    def display(self, scene, dt):
        super().display(scene, dt)
        
class ArenaCrystal(Interactable):
    def __init__(self, position, strata):
        img = pygame.image.load(os.path.join('imgs', 'entities', 'interactables', 'arena-crystal.png')).convert_alpha()
        img = pygame.transform.scale(img, (img.get_width() * 2.5, img.get_height() * 2.5))

        super().__init__(position, img, None, strata, None)
        self.secondary_sprite_id = 'arena_crystal'
        
        self.interactable = False
        self.on_interact_type = 'wave'

        self.img_info = {
            'current_color': None,
            'colors': {
                'wave': [255, 50, 50],
                'ascend': PLAYER_COLOR,
                'inactive': [24, 24, 24]
            },

            'selected_colors': {
                'wave': [255, 100, 100],
                'ascend': PLAYER_COLOR
            },

            'selected_text': {
                'wave': 'next wave',
                'ascend': 'ascend'
            },

            'frame_count': 0
        }
        
    def on_interact(self, scene):
        self.interactable = False

        particles = []
        for _ in range(5):
            pos = [
                self.center_position[0] + random.randint(-100, 100), 
                self.center_position[1] + random.randint(-50, 0)
            ]

            particle = Circle(self.center_position, self.img_info['current_color'], 5, 0)
            particle.set_goal(100, position=pos, radius=0)
            particle.set_easings(position='ease_out_cir')
            particle.set_gravity(-1)

            particle.glow['active'] = True
            particle.glow['size'] = 1.5
            particle.glow['intensity'] = .2

            particles.append(particle)

        scene.add_sprites(particles)

        self.set_position_tween([self.true_position[0], self.true_position[1] + 15], 60, 'ease_out_quint')
        self.img_info['current_color'] = self.img_info['colors']['inactive']

        scene.player.combat_info['health'] = scene.player.combat_info['max_health']
        scene.delay_timers.append([30, scene.wave_handler.new_wave, []])

    def enable(self, scene):
        self.interactable = True

        self.set_position_tween([self.true_position[0], self.true_position[1] - 15], 60, 'ease_out_quint')
        self.img_info['current_color'] = self.img_info['colors'][self.on_interact_type]

        self.selected_text = self.img_info['selected_text'][self.on_interact_type]
        self.selected_color = self.img_info['selected_colors'][self.on_interact_type]

    def set_image(self, dt):
        self.image = self.mask.to_surface(setcolor=self.img_info['current_color'], unsetcolor=(0, 0, 0, 0)).convert_alpha()

        if self.interactable:
            self.rect_offset[1] = round(math.sin(self.img_info['frame_count'] * .02) * 3)
            self.img_info['frame_count'] += 1 * dt        

    def display(self, scene, dt):
        self.set_image(dt)

        self.selected = scene.player.interact_info['sprite'] == self
        if self.selected:
            create_outline_full(self, self.selected_color, scene.entity_surface, 3)

        super().display(scene, dt)

