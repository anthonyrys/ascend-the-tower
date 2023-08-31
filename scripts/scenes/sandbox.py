from scripts.scenes.game_scene import GameScene

from scripts.ui.text_box import TextBox

import pygame

class Sandbox(GameScene):
    def __init__(self, scene_handler, mouse, sprites=None):
        super().__init__(scene_handler, mouse, sprites)

        self.ui_elements.extend([
            TextBox((10, 130), '3: draw regular cards', size=.5),
            TextBox((10, 160), '4: draw stat cards', size=.5),
            TextBox((10, 190), '0: fullscreen', size=.5)
        ])

        self.add_sprites(self.tiles)
        self.add_sprites(self.ui_elements)
        self.add_sprites(self.player)
    
    def on_key_down(self, event):
        super().on_key_down(event)
        
        if self.paused:
            return
        
        if event.key == pygame.K_3:
            cards, text = self.generate_standard_cards()
            if cards and text:
                self.load_card_event(cards, text)

        elif event.key == pygame.K_4:
            cards, text = self.generate_stat_cards()
            if cards and text:
                self.load_card_event(cards, text)

    def on_player_death(self):
        super().on_player_death()

        self.delay_timers.append([90, self.on_scene_end, []])
