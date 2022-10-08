from src.constants import (
    COLORS,
    SCREEN_DIMENSIONS
)

from src.entities.entity import Tags
from src.entities.player import Player
from src.entities.terrain.collidable import Collidable
from src.entities.terrain.barrier import ColorBarrier

from src.misc.camera import BoxCamera
from src.misc.background import Background
from src.scenes.scene import Scene

import pygame

class Sandbox(Scene):
    def __init__(self, surfaces, sprites=...):
        super().__init__(surfaces, sprites)

        player = Player(pygame.Vector2(600, 1125), 2)
        floor = Collidable(pygame.Vector2(500, 1500), pygame.Color(255, 255, 255), pygame.Vector2(3000, 20)) 

        block_a = Collidable(pygame.Vector2(700, 1450), pygame.Color(255, 255, 255), pygame.Vector2(50, 50))  
        block_b = Collidable(pygame.Vector2(900, 1350), pygame.Color(255, 255, 255), pygame.Vector2(50, 50))  
        
        barrier_a = ColorBarrier(pygame.Vector2(500, 1200), pygame.Vector2(250, 100), COLORS[0], player)
        barrier_b = ColorBarrier(pygame.Vector2(950, 1200), pygame.Vector2(250, 50), COLORS[1], player)
        barrier_c = ColorBarrier(pygame.Vector2(1300, 1250), pygame.Vector2(75, 250), COLORS[2], player)
        barrier_d = ColorBarrier(pygame.Vector2(1450, 1250), pygame.Vector2(75, 250), COLORS[0], player)
        barrier_e = ColorBarrier(pygame.Vector2(1700, 1250), pygame.Vector2(150, 250), COLORS[1], player)
        barrier_f = ColorBarrier(pygame.Vector2(2000, 1350), pygame.Vector2(250, 50), COLORS[2], player)

        self.background = Background()
        self.camera = BoxCamera(player)

        self.view = pygame.Surface(SCREEN_DIMENSIONS).get_rect()
        self.sprite_view = pygame.Surface(SCREEN_DIMENSIONS).get_rect()

        self.add_sprites(
            player, floor, 
            block_a, block_b, 
            barrier_a, barrier_b, barrier_c, 
            barrier_d, barrier_e, barrier_f
        )

    def display(self, screen, dt):
        dt = 2 if dt > 2 else dt
        dt = round(dt, 1)

        cam = self.camera.update(self, dt)
        self.sprite_view.x, self.sprite_view.y = cam

        self.background_surface.fill(pygame.Color(0, 0, 0, 0), self.view)
        self.sprite_surface.fill(pygame.Color(0, 0, 0, 0), self.sprite_view)
        self.ui_surface.fill(pygame.Color(0, 0, 0, 0), self.view)

        self.background.display(self.background_surface, dt)

        display_order = self.sort_sprites(self.sprites)
        for _, v in sorted(display_order.items()):
            for sprite in v: 
                if not sprite.active:
                    continue
                
                if sprite.get_tag(Tags.PLAYER) or sprite.get_tag(Tags.PARTICLE) or sprite.get_tag(Tags.BARRIER):
                    sprite.display(self, dt)
                    continue

                sprite.display(self.sprite_surface)
        
        screen.blit(self.background_surface, (0, 0))
        screen.blit(self.sprite_surface, -cam)
        screen.blit(self.ui_surface, (0, 0))

        self.frames += 1
    