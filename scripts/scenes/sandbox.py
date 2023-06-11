'''
Holds the Sandbox class.
'''

from scripts.constants import SCREEN_DIMENSIONS

from scripts.scenes.game_scene import GameScene

from scripts.ui.text_box import TextBox

import pygame
import random

class Sandbox(GameScene):
    def __init__(self, scene_handler, surfaces, mouse, sprites=None):
        super().__init__(scene_handler, surfaces, mouse, sprites)

        del self.tiles['crystal']
        
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
            super().on_wave_complete()

        elif event.key == pygame.key.key_code('4'):
            enemy = random.choice(self.wave_handler.ENEMY_INFO[1])(self.wave_handler.get_spawn_position(), 6)

            self.add_sprites(enemy)

    def on_player_death(self):
        super().on_player_death()

        self.delay_timers.append([90, self.on_scene_end, []])
