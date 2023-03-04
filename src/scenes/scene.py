from src.constants import SCREEN_DIMENSIONS
from src.entities.particle_fx import Particle

import pygame

class Scene:
    def __init__(self, surfaces, mouse, sprites=None):
        self.surfaces = surfaces
        self.background_surface, self.entity_surface, self.ui_surface = self.surfaces
        self.mouse = mouse

        self.view = pygame.Surface(SCREEN_DIMENSIONS).get_rect()

        self.dt_info = {
            'multiplier': 1,
            'frames': 0,
            'max_frames': 0
        }

        self.sprites = sprites if isinstance(sprites, list) else []

        self.frame_count = 0
        self.frame_count_raw = 0

    @staticmethod
    def sort_sprites(sprites):
        display_order = {}
        unlabled = []

        for sprite in sprites:
            if not isinstance(sprite.strata, int):
                unlabled.append(sprite)
                continue

            if sprite.strata in display_order:
                display_order[sprite.strata].append(sprite)

            else:
                display_order[sprite.strata] = list([sprite])

        if unlabled:
            display_order[-1] = []

            for sprite in unlabled:
                if isinstance(sprite, Particle):
                    strata = len(display_order) + 1

                    if strata in display_order:
                        display_order[strata].append(sprite)

                    else:
                        display_order[strata] = list([sprite])
                        
                    continue
                
                display_order[-1].append(sprite)

        return display_order
        
    def display(self, screen, clock, dt):
        ...

    def get_selected_interactable(self):
        ...

    def on_mouse_down(self, event):
        for sprite in self.sprites:
            if not hasattr(sprite, 'on_mouse_down') or not callable(sprite.on_mouse_down):
                continue

            sprite.on_mouse_down(self, event.button)

    def on_mouse_up(self, event):
        for sprite in self.sprites:
            if not hasattr(sprite, 'on_mouse_up') or not callable(sprite.on_mouse_up):
                continue

            sprite.on_mouse_up(self, event.button)

    def on_key_down(self, event):
        for sprite in self.sprites:
            if not hasattr(sprite, 'on_key_down') or not callable(sprite.on_key_down):
                continue

            sprite.on_key_down(self, event.key)

    def on_key_up(self, event):
        for sprite in self.sprites:
            if not hasattr(sprite, 'on_key_up') or not callable(sprite.on_key_up):
                continue

            sprite.on_key_up(self, event.key)

    def set_dt_multiplier(self, multiplier, duration):
        self.dt_info['max_frames'] = duration
        self.dt_info['frames'] = duration

        self.dt_info['multiplier'] = multiplier

    def add_sprites(self, sprites, *args):
        if not isinstance(sprites, list):
            sprites = list([sprites])

        for arg in args: 
            sprites.append(arg)

        for sprite in sprites:
            if not isinstance(sprite, pygame.sprite.Sprite):
                continue
                
            if sprite in self.sprites:
                continue

            self.sprites.append(sprite)

    def del_sprites(self, sprites, *args):
        if not isinstance(sprites, list):
            sprites = list([sprites])

        for arg in args: 
            sprites.append(arg)

        for sprite in sprites:
            if not sprite in self.sprites:
                continue

            self.sprites.remove(sprite)
