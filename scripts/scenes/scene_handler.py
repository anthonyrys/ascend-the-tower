from scripts import (
    SCREEN_COLOR,
    SCREEN_DIMENSIONS,
    FRAME_RATE
)

from scripts.scenes.sandbox import Sandbox

from scripts.ui.card import Card
from scripts.ui.mouse import Mouse

from scripts.utils.inputs import Inputs

import pygame
import time

class SceneHandler:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.fullscreen = False

        self.mouse = Mouse()

        self.current_scene = Sandbox(self, self.mouse)
        self.stored_scenes = []

        self.last_time = time.time()

        Card.init()

    def set_new_scene(self, scene, info):
        self.current_scene = scene(self, self.mouse)

    def update(self):
        delta_time = (time.time() - self.last_time) * FRAME_RATE
        self.last_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    self.fullscreen = not self.fullscreen

                    if self.fullscreen:
                        self.screen = pygame.display.set_mode(SCREEN_DIMENSIONS, pygame.FULLSCREEN|pygame.SCALED)
                    
                    else:
                        self.screen = pygame.display.set_mode(SCREEN_DIMENSIONS)

                else:
                    self.current_scene.on_key_down(event)

            if event.type == pygame.KEYUP:
                self.current_scene.on_key_up(event)

            if event.type == pygame.MOUSEBUTTONDOWN: 
                self.current_scene.on_mouse_down(event)

            if event.type == pygame.MOUSEBUTTONUP: 
                self.current_scene.on_mouse_up(event)

        Inputs.get_keys_pressed()

        self.screen.fill(SCREEN_COLOR)
        self.current_scene.display(self.screen, self.clock, delta_time)

        return False
