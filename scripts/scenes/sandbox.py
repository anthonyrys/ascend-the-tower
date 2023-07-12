from scripts.entities.enemy import RockGolem, StoneSentry, GraniteElemental

from scripts.scenes.game_scene import GameScene

from scripts.ui.text_box import TextBox

from scripts.utils.bezier import presets

import pygame
import random

class Sandbox(GameScene):
    def __init__(self, scene_handler, mouse, sprites=None):
        super().__init__(scene_handler, mouse, sprites)

        self.ui_elements.extend([TextBox((10, 130), '0: fullscreen', size=.5)])

        self.add_sprites(self.tiles)
        self.add_sprites(self.ui_elements)
        self.add_sprites(self.player)
    
    def on_player_death(self):
        super().on_player_death()

        self.delay_timers.append([90, self.on_scene_end, []])
