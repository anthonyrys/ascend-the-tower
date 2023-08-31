from scripts import PLAYER_COLOR

from scripts.entities.entity import Entity

from scripts.visual_fx.particle import Circle

from scripts.entities.particle_fx import Circle

from scripts.tools.spritesheet_loader import load_spritesheet

from scripts.tools.bezier import presets
from scripts.tools import get_sprite_colors

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
    def __init__(self, position, img, dimensions, strata, alpha):
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
    def __init__(self, position, img, dimensions, strata=None, alpha=255):
        if img is None:
            img = load_spritesheet(os.path.join('resources', 'images', 'entities', 'interactables', 'card.png'), scale=2)[0]

        super().__init__(position, img, dimensions, strata, alpha)
        self.secondary_sprite_id = 'standard_card_interactable'
        self.interactable = False

        self.focus_sprites = 'player'

        self.sin_amplifier = 2
        self.sin_frequency = .05

        self.sin_count = 0

        self.delay_timers.append([30, self.set_interactable, []])

    def on_interact(self, scene, sprite):
        cards, text, discard = scene.generate_standard_cards()

        particle = Circle([0, 0], (255, 255, 255), 0, 5, self)
        particle.set_goal(15, position=[0, 0], radius=40, width=1, alpha=0)
        particle.set_beziers(alpha=[*presets['rest'], 0])

        scene.add_sprites(particle)

        if cards and text:
            scene.load_card_event(cards, text, discard)

        scene.del_sprites(self)

    def display(self, scene, dt):
        self.rect_offset[1] = round((self.sin_amplifier * math.sin(self.sin_frequency * (self.sin_count))))
        self.sin_count += 1 * dt

        super().display(scene, dt)

class StatCardInteractable(Interactable):
    def __init__(self, position, img, dimensions, strata=None, alpha=255):
        super().__init__(position, img, dimensions, strata, alpha)
        self.secondary_sprite_id = 'stat_card_interactable'

        self.focus_sprites = 'player'

        self.sin_amplifier = 2
        self.sin_frequency = .05

        self.sin_count = 0

    def on_interact(self, scene, sprite):
        cards, text, discard = scene.generate_stat_cards()

        particle = Circle([0, 0], PLAYER_COLOR, 0, 5, self)
        particle.set_goal(15, position=[0, 0], radius=40, width=1, alpha=0)
        particle.set_beziers(alpha=[*presets['rest'], 0])

        scene.add_sprites(particle)

        if cards and text:
            scene.load_card_event(cards, text, discard)

        scene.del_sprites(self)

    def display(self, scene, dt):
        self.rect_offset[1] = round((self.sin_amplifier * math.sin(self.sin_frequency * (self.sin_count))))
        self.sin_count += 1 * dt

        super().display(scene, dt)

class NextFloorInteractable(Interactable):
    def __init__(self, position, img, dimensions, strata=None, alpha=255):
        super().__init__(position, img, dimensions, strata, alpha)
        self.secondary_sprite_id = 'next_floor_interactable'

        self.focus_sprites = 'player'

        self.sin_amplifier = 3
        self.sin_frequency = .075
        self.sin_count = 0

        self.particle_count = [0, 25]

    def on_interact(self, scene, sprite):
        self.set_interactable()

        if sprite.abilities['primary'].state == 'active':
            sprite.abilities['primary'].end(scene)
        
        sprite.combat_info['immunities']['all'] = 1

        scene.on_floor_clear()

    def display(self, scene, dt):
        self.rect.centery = self.original_rect.centery - round((self.sin_amplifier * math.sin(self.sin_frequency * (self.sin_count))))
        self.sin_count += 1 * dt

        self.particle_count[0] += 1 * dt
        if self.particle_count[0] >= self.particle_count[1]:
            self.particle_count[0] = 0

            cir = Circle(self.rect.center, get_sprite_colors(self)[0], random.randint(5, 7), 0)
            cir.set_goal(90, position=[self.rect.centerx - random.randint(-50, 50), self.rect.centery - random.randint(-100, 100)], radius=0)
            cir.set_beziers(position=[[0, 0], [-1.5, 1.5], [1, 2], [1, 0], 0])
            cir.glow['active'] = True
            cir.glow['size'] = 2
            cir.glow['intensity'] = .25

            scene.add_sprites(cir)

        super().display(scene, dt)
