'''
Baseclass for the game scene.
'''

from scripts.constants import SCREEN_DIMENSIONS
from scripts.entities.particle_fx import Particle

import pygame

class Scene:
    '''
    Variables:
        sprite_list: a single list of all the current sprites.
        
        surfaces: a list of surfaces given by the scene handler.
        mouse: a mouse object.

        view: a pygame surface view of the current screen.

        dt_info: info on how delta time should be percvied.

        sprites: a list of the current sprites within the scene.

        frame_count: the number of frames that has passed in the scene (rounded).
        frame_count_raw: the number of frames that has passed in the scene (not rounded).

        in_menu: whether the scene is in a menu.
        paused: whether the scene is paused.

    Methods:
        sort_sprites: sorts the sprites based on their strata level.

        on_mouse_down: called when the mouse has been pressed.
        on_mouse_down: called when the mouse has been released.

        on_key_down: called when a key is pressed.
        on_key_up: called when a key is released.

        set_dt_multiplier: sets dt_info multiplier for a duration.

        get_sprites: returns a list of sprites based on the given arguments.
        add_sprites: add sprites to the scene.
        del_sorites: deletes sprites from the scene.
    '''

    def __init__(self, scene_handler, surfaces, mouse, sprites=None):
        self.scene_handler = scene_handler
        
        self.surfaces = surfaces
        self.background_surface, self.entity_surface, self.ui_surface = self.surfaces
        self.mouse = mouse

        self.view = pygame.Surface(SCREEN_DIMENSIONS).get_rect()

        self.dt_info = {
            'multiplier': 1,
            'frames': 0,
            'max_frames': 0
        }

        self.sprites = sprites if isinstance(sprites, dict) else {}

        self.frame_count = 0
        self.frame_count_raw = 0

        self.in_menu = False
        self.paused = False

    @property
    def sprite_list(self):
        sprite_list = []

        for value in self.sprites.values():
            for sprites in value.values():
                sprite_list.extend(sprites)

        return sprite_list
    
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

    def on_mouse_down(self, event):
        for sprite in self.sprite_list:
            if not hasattr(sprite, 'on_mouse_down') or not callable(sprite.on_mouse_down):
                continue

            sprite.on_mouse_down(self, event.button)

    def on_mouse_up(self, event):
        for sprite in self.sprite_list:
            if not hasattr(sprite, 'on_mouse_up') or not callable(sprite.on_mouse_up):
                continue

            sprite.on_mouse_up(self, event.button)

    def on_key_down(self, event):
        for sprite in self.sprite_list:
            if not hasattr(sprite, 'on_key_down') or not callable(sprite.on_key_down):
                continue

            sprite.on_key_down(self, event.key)

    def on_key_up(self, event):
        for sprite in self.sprite_list:
            if not hasattr(sprite, 'on_key_up') or not callable(sprite.on_key_up):
                continue

            sprite.on_key_up(self, event.key)

    def set_dt_multiplier(self, multiplier, duration):
        self.dt_info['max_frames'] = duration
        self.dt_info['frames'] = duration

        self.dt_info['multiplier'] = multiplier

    def get_sprites(self, sprite_id, secondary_sprite_id=None, include=[], exclude=[]): 
        if isinstance(sprite_id, list):
            sprite_list = []
            for spr_id in sprite_id:
                if spr_id not in self.sprites:
                    continue

                for key, value in self.sprites[spr_id].items():
                    sprite_list.extend(value) 

            return sprite_list

        if sprite_id not in self.sprites.keys():
            return []
        
        sprite_list = []
        include = self.sprites[sprite_id].keys() if not include else include

        if secondary_sprite_id is None:
            for key, value in self.sprites[sprite_id].items():
                if key not in include:
                    continue

                if key in exclude:
                    continue

                sprite_list.extend(value)

        else:
            if secondary_sprite_id not in self.sprites[sprite_id].keys():
                return []

            return self.sprites[sprite_id][secondary_sprite_id]

        return sprite_list

    def add_sprites(self, sprites, *args):
        if not isinstance(sprites, list):
            sprites = list([sprites])

        for arg in args: 
            sprites.append(arg)

        for sprite in sprites:
            if not isinstance(sprite, pygame.sprite.Sprite):
                continue
                
            if sprite in self.sprite_list:
                continue

            sprite_id = sprite.sprite_id
            secondary_sprite_id = sprite.secondary_sprite_id

            if sprite_id is None:
                continue

            if sprite_id not in self.sprites.keys():
                self.sprites[sprite_id] = {'default': []}

            if secondary_sprite_id not in self.sprites[sprite_id].keys() and secondary_sprite_id is not None:
                self.sprites[sprite_id][secondary_sprite_id] = []
            
            if secondary_sprite_id is None:
                self.sprites[sprite_id]['default'].append(sprite)
            else:
                self.sprites[sprite_id][secondary_sprite_id].append(sprite)

    def del_sprites(self, sprites, *args):
        if not isinstance(sprites, list):
            sprites = list([sprites])

        for arg in args: 
            sprites.append(arg)

        for sprite in sprites:
            if not sprite in self.sprite_list:
                continue

            sprite_id = sprite.sprite_id
            secondary_sprite_id = sprite.secondary_sprite_id

            if secondary_sprite_id is None:
                self.sprites[sprite_id]['default'].remove(sprite)

            else:
                self.sprites[sprite_id][secondary_sprite_id].remove(sprite)

                if len(self.sprites[sprite_id][secondary_sprite_id]) == 0:
                    del self.sprites[sprite_id][secondary_sprite_id]

                if len([i for s in [v for v in self.sprites[sprite_id].values()] for i in s]) == 0:
                    del self.sprites[sprite_id]