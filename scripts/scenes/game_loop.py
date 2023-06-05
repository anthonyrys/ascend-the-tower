'''
Holds the main Scene for the game.
'''

from scripts.constants import SCREEN_DIMENSIONS
from scripts.engine import BoxCamera

from scripts.entities.player import Player
from scripts.entities.tiles import Barrier, Floor, Ceiling

from scripts.scenes.game_scene import GameScene

from scripts.ui.text_box import TextBox

import pygame

class GameLoop(GameScene):
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

        self.wave_handler.new_level()
        self.delay_timers.append([30, self.wave_handler.new_wave, []])

        self.add_sprites(self.player)

        for sprite_list in self.tiles.values():
            for sprite in sprite_list:
                self.add_sprites(sprite)

        self.add_sprites(self.ui_elements)

    def on_player_death(self):
        super().on_player_death()

        self.delay_timers.append([90, self.on_scene_end, []])

    def remove_cards(self, selected_card, cards):
        if not super().remove_cards(selected_card, cards):
            return

        self.player.set_stat('max_health', round(self.card_info['stat_info'][0]['value'][0] * .5), True)
        self.player.set_stat('base_damage', round(self.card_info['stat_info'][1]['value'][0] * .5), True)

        self.player.combat_info['health'] = self.player.combat_info['max_health']

        self.delay_timers.append([45, self.wave_handler.new_wave, []])

    def display(self, screen, clock, dt):
        self.wave_handler.update(dt)

        super().display(screen, clock, dt)
