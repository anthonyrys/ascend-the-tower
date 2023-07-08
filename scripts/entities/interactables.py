from scripts.entities.entity import Entity

from scripts.services import load_spritesheet

from scripts.utils.bezier import presets

import pygame
import random
import inspect
import math
import sys
import os

def get_all_interactables():
    interactable_list = [t for t in inspect.getmembers(sys.modules[__name__], inspect.isclass)]
			
    return interactable_list

class Interactable(Entity):
    def __init__(self, position, img, dimensions, strata, alpha=255):
        super().__init__(position, img, dimensions, strata, alpha)
        self.sprite_id = 'interactable'

        self.interactable = True
        self.focus_sprites = []
    
    def on_interact(self, scene, sprite):
        ...
    
    def set_interactable(self):
        self.interactable = not self.interactable

    def display(self, scene, dt):
        if not scene.paused and not scene.in_menu:
            if self.focus_sprites and self.interactable:
                for sprite in scene.get_sprites(self.focus_sprites):
                    if not self.rect.colliderect(sprite.rect):
                        continue

                    self.on_interact(scene, sprite)
                    break

        super().display(scene, dt)

class StandardCardInteractable(Interactable):
    def __init__(self, position, strata, alpha=255):
        image = load_spritesheet(os.path.join('imgs', 'entities', 'interactables', 'card.png'), scale=2)[0]
        super().__init__(position, image, None, strata, alpha)
        self.secondary_sprite_id = 'standard_card_interactable'
        self.interactable = False

        self.focus_sprites = 'player'

        self.sin_amplifier = 2
        self.sin_frequency = .05

        self.sin_count = 0

        bezier = [[0, 0], [.5, 1.5], [1, 0], [1, 0]]
        rand = random.randint(-100, 100)
        
        self.set_x_bezier(position[0] + rand * 2, 75, [*bezier, 0])
        self.set_y_bezier(position[1] - abs(rand), 75, [*bezier, 1])

        self.delay_timers.append([30, self.set_interactable, []])

    def on_interact(self, scene, sprite):
        cards, text = scene.generate_standard_cards()

        scene.in_menu = True
        scene.paused = True

        scene.scene_fx['&dim']['bezier'] = presets['ease_out']
        scene.scene_fx['&dim']['type'] = 'in'

        scene.scene_fx['&dim']['amount'] = .75
        scene.scene_fx['&dim']['frames'][1] = 30
            
        scene.scene_fx['&dim']['threshold'] = 1

        for frame in scene.ui_elements:
            frame.image.set_alpha(100)

        scene.add_sprites(cards)
        scene.add_sprites(text)

        scene.del_sprites(self)

    def display(self, scene, dt):
        self.rect_offset[1] = round((self.sin_amplifier * math.sin(self.sin_frequency * (self.sin_count))))
        self.sin_count += 1 * dt

        super().display(scene, dt)

class StatCardInteractable(Interactable):
    def __init__(self, position, img, dimensions, strata=None):
        super().__init__(position, img, dimensions, strata)
        self.secondary_sprite_id = 'stat_card_interactable'

        self.focus_sprites = 'player'

        self.sin_amplifier = 2
        self.sin_frequency = .05

        self.sin_count = 0

    def on_interact(self, scene, sprite):
        cards, text = scene.generate_stat_cards()

        scene.in_menu = True
        scene.paused = True

        scene.scene_fx['&dim']['bezier'] = presets['ease_out']
        scene.scene_fx['&dim']['type'] = 'in'

        scene.scene_fx['&dim']['amount'] = .75
        scene.scene_fx['&dim']['frames'][1] = 30
        
        scene.scene_fx['&dim']['threshold'] = 1

        for frame in scene.ui_elements:
            frame.image.set_alpha(100)

        scene.add_sprites(cards)
        scene.add_sprites(text)

        scene.del_sprites(self)

    def display(self, scene, dt):
        self.rect_offset[1] = round((self.sin_amplifier * math.sin(self.sin_frequency * (self.sin_count))))
        self.sin_count += 1 * dt

        super().display(scene, dt)