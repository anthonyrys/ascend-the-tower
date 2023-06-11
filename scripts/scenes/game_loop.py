'''
Holds the main Scene for the game.
'''

from scripts.constants import SCREEN_DIMENSIONS

from scripts.scenes.game_scene import GameScene

from scripts.ui.text_box import TextBox

import pygame

class GameLoop(GameScene):
    def __init__(self, scene_handler, surfaces, mouse, sprites=None):
        super().__init__(scene_handler, surfaces, mouse, sprites)

        self.tiles['crystal'].enable(self)
        
        self.ui_elements.extend(self.player.get_ui_elements())
        self.ui_elements.append(TextBox((40, SCREEN_DIMENSIONS[1] - 50), '0: fullscreen', size=.5))

        self.wave_handler.new_area()

        self.add_sprites(self.player)

        for sprite_list in self.tiles.values():
            if not isinstance(sprite_list, list):
                self.add_sprites(sprite_list)
                continue
            
            for sprite in sprite_list:
                self.add_sprites(sprite)

        self.add_sprites(self.ui_elements)

    def on_player_death(self):
        super().on_player_death()

        self.delay_timers.append([90, self.on_scene_end, []])

    def remove_cards(self, selected_card, cards, flavor_text):
        if not super().remove_cards(selected_card, cards, flavor_text):
            return

        self.player.set_stat('max_health', round(self.card_info['stat_info'][0]['value'][0] * .5), True)
        self.player.set_stat('base_damage', round(self.card_info['stat_info'][1]['value'][0] * .5), True)

        self.tiles['crystal'].enable(self)

    def display(self, screen, clock, dt):
        self.wave_handler.update(dt)

        super().display(screen, clock, dt)
