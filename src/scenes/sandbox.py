from src.engine import BoxCamera

from src.entities.enemy import Stelemental
from src.entities.player import Player
from src.entities.tiles import Block, Platform, Ramp, Floor

from src.scenes.scene import Scene

from src.ui.healthbar import Healthbar
from src.ui.expbar import Expbar

import pygame
import random
import os

class Sandbox(Scene):
    def __init__(self, surfaces, mouse, sprites=None):
        super().__init__(surfaces, mouse, sprites)

        self.in_menu = False

        self.player = Player((615, 1200), 4)

        self.camera = BoxCamera(self.player)
        self.camera_offset = [0, 0]
        
        self.ui = {
            'healthbar': Healthbar(self.player),
            'expbar': Expbar(self. player),
        }

        self.player.healthbar = self.ui['healthbar']

        self.tiles = {
            'floors': [Floor((0, 1500), (155, 155, 255), (10000, 100), 5)],

            'walls': [
                Block((-20, 0), (155, 155, 255), (20, 1500), 5),        
                Block((10000, 0), (155, 155, 255), (20, 1500), 5)
            ],

            'blocks': [
                Block((596, 1405), (155, 155, 255), (48, 96), 5),
                Block((836, 1405), (155, 155, 255), (48, 96), 5),
                Block((196, 1453), (155, 155, 255), (96, 48), 5), 
                Block((1400, 1452), (155, 155, 255), (48, 48), 5),
                Block((1600, 1404), (155, 155, 255), (48, 48), 5), 
                Block((1800, 1356), (155, 155, 255), (48, 48), 5), 
                Block((2000, 1308), (155, 155, 255), (48, 48), 5),   
                Block((2800, 1452), (155, 155, 255), (48, 48), 5), 
                Block((2600, 1404), (155, 155, 255), (48, 48), 5),
                Block((2400, 1356), (155, 155, 255), (48, 48), 5),
                Block((2200, 1308), (155, 155, 255), (48, 48), 5) 
            ],

            'ramps': [
                Ramp((500, 1405), 0, 'right', (155, 155, 255), 5),
                Ramp((884, 1405), 0, 'left', (155, 155, 255), 5),
                Ramp((100, 1405), 1, 'right', (155, 155, 255), 5),
                Ramp((292, 1405), 1, 'left', (155, 155, 255), 5)
            ],

            'platforms': [Platform((644, 1405), (125, 125, 255), (192, 8), 3)]
        }

        self.add_sprites(self.player)

        for sprite_list in self.tiles.values():
            for sprite in sprite_list:
                self.add_sprites(sprite)

        for sprite in self.ui.values():
            self.add_sprites(sprite)

        self.enemy_info = [[120, 60], [0, 3]]

    def display(self, screen, clock, dt):
        if self.dt_info['frames'] > 0:
            dt *= self.dt_info['multiplier']
            self.dt_info['frames'] -= 1

        dt = 3 if dt > 3 else dt
        dt = round(dt, 1)
        
        entity_view = pygame.Rect(
            self.camera_offset[0] - self.view.width * .5, self.camera_offset[1] - self.view.height * .5, 
            self.view.width * 2, self.view.height * 2
        )

        self.background_surface.fill((0, 0, 0, 255), self.view)
        self.entity_surface.fill((0, 0, 0, 255), entity_view)
        self.ui_surface.fill((0, 0, 0, 0), self.view)

        self.enemy_info[1][0] = len([s for s in self.sprites if isinstance(s, Stelemental)])
        if self.enemy_info[0][0] >= self.enemy_info[0][1]:
            self.enemy_info[0][0] = 0

            if self.enemy_info[1][0] < self.enemy_info[1][1]:
                self.add_sprites(Stelemental((random.randint(800, 1400), random.randint(1000, 1600)), 6))

        self.enemy_info[0][0] += 1 * dt

        display_order = self.sort_sprites(self.sprites)
        for _, v in sorted(display_order.items()):
            for sprite in v: 
                if not sprite.active:
                    continue

                sprite.display(self, dt)

        self.camera_offset = self.camera.update(dt)
        self.mouse.display(self)
        
        screen.blit(self.background_surface, (0, 0))
        screen.blit(self.entity_surface, (-self.camera_offset[0], -self.camera_offset[1]))
        screen.blit(self.ui_surface, (0, 0))

        self.frame_count_raw += 1 * dt
        self.frame_count = round(self.frame_count_raw)