from scripts import SCREEN_DIMENSIONS

from scripts.visual_fx.particle import Particle

from scripts.ui.text_box import TextBox

import pygame

class Scene:
    def __init__(self, scene_handler, mouse, sprites=None):
        self.scene_handler = scene_handler
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

        def tick(d):
            for _, v in d.items():
                if isinstance(v, list):
                    sprite_list.extend(v)
                    continue

                tick(v)

        tick(self.sprites)

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
        fps_surface = TextBox.create_text_line('default', round(clock.get_fps()))
        fps_position = [SCREEN_DIMENSIONS[0] - 5, 5]

        screen.blit(fps_surface, fps_surface.get_rect(topright=fps_position))

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