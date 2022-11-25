from src.entities.interactable import Interactable
from src.particle_fx import Particle

import pygame

class Scene():
    def __init__(self, surfaces, mouse, sprites=None):
        self.surfaces = surfaces
        self.background_surface, self.entity_surface, self.ui_surface = self.surfaces
        self.mouse = mouse

        self.paused = False

        self.sprites = sprites if isinstance(sprites, list) else list()
        self.frames = 0
        self.raw_frames = 0

    @staticmethod
    def sort_sprites(sprites):
        display_order = dict()
        unlabled = list()

        for sprite in sprites:
            if not isinstance(sprite.strata, int):
                unlabled.append(sprite)
                continue

            if sprite.strata in display_order:
                display_order[sprite.strata].append(sprite)

            else:
                display_order[sprite.strata] = list([sprite])

        if unlabled:
            display_order[-1] = list()

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
        
    # <overridden by child classes>
    def display(self, screen):
        ...

    def get_selected_interactable(self):
        for interactable in [s for s in self.sprites if isinstance(s, Interactable)]:
            if not interactable.selected:
                continue
            
            return interactable

    def on_mouse_down(self, event):
        if event.button == 1:
            for sprite in self.sprites:
                if not hasattr(sprite, 'on_mouse_down') or not callable(sprite.on_mouse_down):
                    continue

                sprite.on_mouse_down(self)

    def on_mouse_up(self, event):
        if event.button == 1:
            for sprite in self.sprites:
                if not hasattr(sprite, 'on_mouse_up') or not callable(sprite.on_mouse_up):
                    continue

                sprite.on_mouse_up(self)

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
