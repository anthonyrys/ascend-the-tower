from src.engine import Camera

from src.entities.tiles import Block, Platform, Ramp, DamageTile
from src.entities.player import Player

from src.scenes.scene import Scene

import pygame
import os

class Sandbox(Scene):
    def __init__(self, surfaces, mouse, sprites=None):
        super().__init__(surfaces, mouse, sprites)

        self.player = Player((615, 1200), 4)

        self.camera = Camera.Box(self.player)
        self.camera_offset = [0, 0]
        
        floor = Block((0, 1500), (155, 155, 255), (10000, 50), 5) 

        wall_a = Block((-20, 0), (155, 155, 255), (20, 1500), 5)
        wall_b = Block((10000, 0), (155, 155, 255), (20, 1500), 5)

        block_a = Block((596, 1405), (155, 155, 255), (48, 96), 5)  
        block_b = Block((836, 1405), (155, 155, 255), (48, 96), 5)  
        block_c = Block((196, 1453), (155, 155, 255), (96, 48), 5)  

        ramp_a = Ramp((500, 1405), 0, 'right', (155, 155, 255), 5)
        ramp_b = Ramp((884, 1405), 0, 'left', (155, 155, 255), 5)
        ramp_c = Ramp((100, 1405), 1, 'right', (155, 155, 255), 5)
        ramp_d = Ramp((292, 1405), 1, 'left', (155, 155, 255), 5)

        platform = Platform((644, 1405), (125, 125, 255), (192, 8), 3)

        damage_a = DamageTile((2000, 1405), (255, 0, 0), (100, 100), 3)

        self.add_sprites(
            self.player,
            floor, 
            wall_a, wall_b,
            block_a, block_b, block_c,
            platform,
            ramp_a, ramp_b, ramp_c, ramp_d,
            damage_a
        )

    def display(self, screen, clock, dt):
        if self.dt_info['frames'] > 0:
            dt *= self.dt_info['multiplier']
            self.dt_info['frames'] -= 1

        dt = 3 if dt > 3 else dt
        dt = round(dt, 1)

        self.background_surface.fill((0, 0, 0, 255), self.view)
        self.entity_surface.fill((0, 0, 0, 255))
        self.ui_surface.fill((0, 0, 0, 0), self.view)

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
        