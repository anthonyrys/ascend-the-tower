'''
Holds the Sandbox class.
'''

from scripts.constants import SCREEN_DIMENSIONS
from scripts.engine import BoxCamera

from scripts.entities.player import Player
from scripts.entities.tiles import Barrier, Floor, Ceiling

from scripts.scenes.game_scene import GameScene

from scripts.ui.text_box import TextBox

import pygame
import random

class Sandbox(GameScene):
    def __init__(self, scene_handler, surfaces, mouse, sprites=None):
        super().__init__(scene_handler, surfaces, mouse, sprites)

        self.tiles = {
            'barrier_y': [
                Floor((0, 1500), (255, 255, 255, 0), (250, 250), 1),
                Ceiling((0, 0), (255, 255, 255, 0), (250, 250), 1)
            ],

            'barrier_x': [
                Barrier((250, 0), (255, 255, 255, 0), (250, 250), ['player'], 1),        
                Barrier((4500, 0), (255, 255, 255, 0), (250, 250), ['player'], 1)
            ],

            'floor': [
                Floor((0, 1500), (255, 255, 255), (5000, 25), 1)
            ],
        }

        self.player = Player((self.tiles['floor'][0].center_position[0], 1200), 4)

        self.camera = BoxCamera(self.player)
        self.camera_offset = [0, 0]

        self.ui_elements.extend(self.player.get_ui_elements())
        self.ui_elements.append(TextBox((40, SCREEN_DIMENSIONS[1] - 50), '0: fullscreen', size=.5))
        self.ui_elements.append(TextBox((40, SCREEN_DIMENSIONS[1] - 100), '3: draw cards', size=.5))
        self.ui_elements.append(TextBox((40, SCREEN_DIMENSIONS[1] - 150), '4: spawn enemy', size=.5))

        self.add_sprites(self.player)

        for sprite_list in self.tiles.values():
            for sprite in sprite_list:
                self.add_sprites(sprite)

        self.add_sprites(self.ui_elements)

    def on_key_down(self, event):
        super().on_key_down(event)
        
        if self.paused:
            return
        
        if event.key == pygame.key.key_code('3'):
            cards = self.generate_stat_cards()
            self.card_info['overflow'].append([self.generate_standard_cards, []])

            if cards:
                self.in_menu = True
                self.paused = True

                self.scene_fx['entity_dim']['easing'] = 'ease_out_quint'
                self.scene_fx['entity_dim']['type'] = 'in'

                self.scene_fx['entity_dim']['amount'] = .75
                self.scene_fx['entity_dim']['frames'][1] = 30

                for frame in self.ui_elements:
                    frame.image.set_alpha(100)
                
                self.add_sprites(cards)

        elif event.key == pygame.key.key_code('4'):
            enemy = random.choice(self.wave_handler.ENEMY_INFO[1])(self.wave_handler.get_spawn_position(), 6)

            self.add_sprites(enemy)

    def on_player_death(self):
        super().on_player_death()

        self.delay_timers.append([90, self.on_scene_end, []])
