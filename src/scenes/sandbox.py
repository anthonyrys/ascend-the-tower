from src.constants import (
    COLORS,
    SCREEN_DIMENSIONS
)

from src.engine import Camera

from src.entities.player import Player
from src.entities.tile import Tile
from src.entities.barrier import Barrier
from src.entities.platform import Platform
from src.entities.ramp import Ramp
from src.entities.block import Block

from src.scenes.scene import Scene

import pygame

class Sandbox(Scene):
    def __init__(self, surfaces, mouse, sprites=None):
        super().__init__(surfaces, mouse, sprites)

        self.player = Player((615, 1200), 4)
        self.camera = Camera.Box(self.player)
        self.camera_offset = [0, 0]

        self.dt_multiplier = 1 
        self.dt_frames, self.dt_frames_max = 0, 0

        self.view = pygame.Surface(SCREEN_DIMENSIONS).get_rect()
        self.entity_view = pygame.Rect(0, 0, SCREEN_DIMENSIONS[0] * 3, SCREEN_DIMENSIONS[1] * 3)

        self.pause_surface = pygame.Surface(SCREEN_DIMENSIONS).convert_alpha()
        self.pause_surface.fill((0, 0, 0, 75))

        floor = Tile((0, 1500), (255, 255, 255), (5000, 20), 5) 

        wall_a = Tile((-20, 0), (255, 255, 255), (20, 1500), 5)
        wall_b = Tile((5000, 0), (255, 255, 255), (20, 1500), 5)

        block_a = Tile((596, 1405), (255, 255, 255), (48, 96), 5)  
        block_b = Tile((836, 1405), (255, 255, 255), (48, 96), 5)  
        block_c = Tile((196, 1453), (255, 255, 255), (96, 48), 5)  
        
        ramp_a = Ramp((500, 1405), 0, 'right', 5)
        ramp_b = Ramp((884, 1405), 0, 'left', 5)
        ramp_c = Ramp((100, 1405), 1, 'right', 5)
        ramp_d = Ramp((292, 1405), 1, 'left', 5)

        barrier_a = Barrier((500, 1000), (250, 100), COLORS[0], self.player, 1)
        barrier_b = Barrier((950, 1200), (250, 50), COLORS[1], self.player, 1)
        barrier_c = Barrier((1300, 1250), (75, 250), COLORS[2], self.player, 1)

        platform = Platform((644, 1405), (225, 225, 225), (192, 16), 3)  

        self.add_sprites(
            self.player, 
            floor, 
            wall_a, wall_b,
            block_a, block_b, block_c,
            barrier_a, barrier_b, barrier_c,
            platform,
            ramp_a, ramp_b, ramp_c, ramp_d
        )

        for i in range(3):
            self.add_sprites(
                Block((1400 + (i * 100), 1250), (30, 30), 2)
            )

    def set_dt_multiplier(self, duration, multiplier):
        self.dt_frames_max = duration
        self.dt_frames = duration

        self.dt_multiplier = multiplier

    def display(self, screen, dt):
        if self.dt_frames > 0:
            dt *= self.dt_multiplier
            self.dt_frames -= 1

        dt = 3 if dt > 3 else dt
        dt = round(dt, 1)

        self.background_surface.fill((0, 0, 0, 0), self.view)
        self.entity_surface.fill((0, 0, 0, 0), self.entity_view)
        self.ui_surface.fill((0, 0, 0, 0), self.view)

        display_order = self.sort_sprites(self.sprites)
        for _, v in sorted(display_order.items()):
            for sprite in v: 
                if not sprite.active:
                    continue

                sprite.display(self, dt)

        if not self.paused:
            self.camera_offset = self.camera.update(dt)

        else:
            self.entity_surface.blit(self.pause_surface, self.camera_offset)

        self.mouse.display(self, self.player)

        self.entity_view[0] = self.camera_offset[0] - SCREEN_DIMENSIONS[0]
        self.entity_view[1] = self.camera_offset[1] - SCREEN_DIMENSIONS[1]
        
        
        screen.blit(self.background_surface, (0, 0))
        screen.blit(self.entity_surface, (-self.camera_offset[0], -self.camera_offset[1]))
        screen.blit(self.ui_surface, (0, 0))

        self.raw_frames += 1 * dt
        self.frames = round(self.raw_frames)
    