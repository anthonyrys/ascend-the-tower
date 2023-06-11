'''
Holds the handler for the scenes of the game.
'''

from scripts.engine import Inputs
from scripts.constants import (
    SCREEN_COLOR,
    SCREEN_DIMENSIONS,
    FRAME_RATE
)

from scripts.scenes.game_loop import GameLoop

from scripts.ui.card import Card
from scripts.ui.mouse import Mouse

import pygame
import time

class SceneHandler:
    '''
    Variables:
        screen: the current window.
        clock: a pygame clock object.
        fullscreen: whether the screen is fullscreen.

        mouse: initialized mouse class.

        background_surface: a pygame surface used for the background.
        entity_surface: a pygame surface used for entities.
        ui_surface: a pygame surface used for frames.

        current_scene: the current scene
        stored_scenes: a list of scenes used for later retrieval.

        last_time: the last time assigned to the variable; used for delta time calculation.

    Methods:
        set_new_scene(): sets the new scene and store the old one.
    '''

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.fullscreen = False

        self.mouse = Mouse()

        self.background_surface = pygame.Surface((10000, 10000), pygame.SRCALPHA).convert_alpha()
        self.entity_surface = pygame.Surface((10000, 10000), pygame.SRCALPHA).convert_alpha()
        self.ui_surface = pygame.Surface((2000, 2000), pygame.SRCALPHA).convert_alpha()

        self.current_scene = GameLoop(self, [self.background_surface, self.entity_surface, self.ui_surface], self.mouse)
        self.stored_scenes = []

        self.last_time = time.time()

        Card.init()

    def set_new_scene(self, scene, info):
        self.current_scene = scene(self, [self.background_surface, self.entity_surface, self.ui_surface], self.mouse)

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
