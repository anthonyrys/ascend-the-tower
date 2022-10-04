from src.constants import (
    SCREEN_COLOR
)
from src.scenes.sandbox import Sandbox

import pygame
import time

class Handler():
    def __init__(self, screen):
        self.screen = screen

        self.background_surface = pygame.Surface(pygame.Vector2(2500, 2500), pygame.SRCALPHA).convert_alpha()
        self.sprite_surface = pygame.Surface(pygame.Vector2(3500, 3500), pygame.SRCALPHA).convert_alpha()
        self.ui_surface = pygame.Surface(pygame.Vector2(2000, 2000), pygame.SRCALPHA).convert_alpha()

        self.current_scene = Sandbox([self.background_surface, self.sprite_surface, self.ui_surface])
        self.stored_scenes = list()

        self.last_time = time.time()

    def new_scene(self):
        ...

    def update(self):
        # delta_time = (time.time() - self.last_time) * FRAME_RATE
        self.last_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True

            if event.type == pygame.MOUSEBUTTONDOWN: 
                pass

            if event.type == pygame.MOUSEBUTTONUP: 
                pass

            if event.type == pygame.KEYDOWN:
                self.current_scene.on_keydown(event)

            if event.type == pygame.KEYUP:
                self.current_scene.on_keyup(event)

        self.screen.fill(SCREEN_COLOR)
        self.current_scene.display(self.screen)

        return False
