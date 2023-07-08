from scripts.entities.enemy import RockGolem, StoneSentry, GraniteElemental

from scripts.scenes.game_scene import GameScene

from scripts.ui.text_box import TextBox

from scripts.utils.bezier import presets

import pygame
import random

class Sandbox(GameScene):
    def __init__(self, scene_handler, mouse, sprites=None):
        super().__init__(scene_handler, mouse, sprites)

        self.ui_elements.extend([
            TextBox((10, 130), '3: spawn enemy', size=.5),
            TextBox((10, 160), '0: fullscreen', size=.5)
        ])

        self.add_sprites(self.tiles)
        self.add_sprites(self.ui_elements)
        self.add_sprites(self.player)

    def on_key_down(self, event):
        super().on_key_down(event)
        
        if self.paused:
            return
        
        if event.key == pygame.K_3:
            enemy = random.choice([RockGolem, StoneSentry, GraniteElemental])(self.mouse.entity_pos, 6)
            self.add_sprites(enemy)

    def on_player_death(self):
        super().on_player_death()

        self.delay_timers.append([90, self.on_scene_end, []])
