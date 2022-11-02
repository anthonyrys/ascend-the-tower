from src.constants import (
    COLORS,
    SCREEN_DIMENSIONS
)

from src.engine import Camera

from src.entities.player import Player
from src.entities.tile import Tile
from src.entities.barrier import Barrier
from src.entities.grass import Grass
from src.entities.platform import Platform
from src.entities.ramp import Ramp

from src.scenes.scene import Scene

import pygame

class Sandbox(Scene):
    def __init__(self, surfaces, mouse, sprites=None):
        super().__init__(surfaces, mouse, sprites)

        self.player = Player(pygame.Vector2(615, 1200), 2)
        floor = Tile(pygame.Vector2(0, 1500), pygame.Color(255, 255, 255), pygame.Vector2(5000, 20), 4) 

        block_a = Tile(pygame.Vector2(596, 1405), pygame.Color(255, 255, 255), pygame.Vector2(48, 96), 4)  
        block_b = Tile(pygame.Vector2(836, 1405), pygame.Color(255, 255, 255), pygame.Vector2(48, 96), 4)  
        block_c = Tile(pygame.Vector2(196, 1453), pygame.Color(255, 255, 255), pygame.Vector2(96, 48), 4)  
        
        ramp_a = Ramp(pygame.Vector2(500, 1405), 0, 'right', 4)
        ramp_b = Ramp(pygame.Vector2(884, 1405), 0, 'left', 4)
        ramp_c = Ramp(pygame.Vector2(100, 1405), 1, 'right', 4)
        ramp_d = Ramp(pygame.Vector2(292, 1405), 1, 'left', 4)

        barrier_a = Barrier(pygame.Vector2(500, 1000), pygame.Vector2(250, 100), COLORS[0], self.player, 1)
        barrier_b = Barrier(pygame.Vector2(950, 1200), pygame.Vector2(250, 50), COLORS[1], self.player, 1)
        barrier_c = Barrier(pygame.Vector2(1300, 1250), pygame.Vector2(75, 250), COLORS[2], self.player, 1)

        platform_a = Platform(pygame.Vector2(644, 1405), pygame.Color(225, 225, 225), pygame.Vector2(192, 16), 1)  
        
        self.camera = Camera.Box(self.player)

        self.view = pygame.Surface(SCREEN_DIMENSIONS).get_rect()
        self.entity_view = pygame.Rect(0, 0, SCREEN_DIMENSIONS[0] * 2, SCREEN_DIMENSIONS[1] * 3)

        self.add_sprites(
            self.player, floor, 
            block_a, block_b, block_c,
            barrier_a, barrier_b, barrier_c,
            platform_a,
            ramp_a, ramp_b, ramp_c, ramp_d
        )

        for i in range(250):
            self.add_sprites(
                Grass(pygame.Vector2(1500 + (i * 9), 1500), 3, self.player)
            )

    def display(self, screen, dt):
        dt = 3 if dt > 3 else dt
        dt = round(dt, 1)

        self.background_surface.fill(pygame.Color(0, 0, 0, 0), self.view)
        self.entity_surface.fill(pygame.Color(0, 0, 0, 0), self.entity_view)
        self.ui_surface.fill(pygame.Color(0, 0, 0, 0), self.view)

        display_order = self.sort_sprites(self.sprites)
        for _, v in sorted(display_order.items()):
            for sprite in v: 
                if not sprite.active:
                    continue

                sprite.display(self, dt)
        
        self.mouse.display(self, self.player)

        cam = self.camera.update(dt)
        self.entity_view.x, self.entity_view.y = cam.x - SCREEN_DIMENSIONS[0], cam.y - SCREEN_DIMENSIONS[1]
        
        screen.blit(self.background_surface, (0, 0))
        screen.blit(self.entity_surface, -cam)
        screen.blit(self.ui_surface, (0, 0))

        self.frames += 1
    