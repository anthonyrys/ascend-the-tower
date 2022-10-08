from src.constants import SCREEN_DIMENSIONS

import pygame
import random
import math

class TweenCamera():
    def __init__(self, position, camera, frames):
        ...
        
    def update(self, scene):
        ...
        
class BoxCamera():
    def __init__(self, focus):
        self.focus = focus

        self.box_dimensions = pygame.Vector2(555, 265)
        self.box = pygame.Rect(
            self.box_dimensions.x,
            self.box_dimensions.y,

            SCREEN_DIMENSIONS.x - (self.box_dimensions.x * 2),
            SCREEN_DIMENSIONS.y - (self.box_dimensions.y * 2)
        )

        self.camera_shake_frames_max, self.camera_shake_frames = 0, 0
        self.camera_shake_intensity = 10

    def set_camera_shake(self, frames):
        self.camera_shake_frames_max = frames
        self.camera_shake_frames = frames

    def update(self, scene, dt):
        camera_shake = pygame.Vector2()

        if self.focus.rect.left < self.box.left:
            self.box.left = self.focus.rect.left

        elif self.focus.rect.right > self.box.right:
            self.box.right = self.focus.rect.right

        if self.focus.rect.bottom > self.box.bottom:
            self.box.bottom = self.focus.rect.bottom

        elif self.focus.rect.top < self.box.top:
            self.box.top = self.focus.rect.top

        if self.camera_shake_frames > 0:
            abs_prog = self.camera_shake_frames / self.camera_shake_frames_max
            intensity = round((self.camera_shake_intensity) * (1 - math.cos((abs_prog * math.pi) / 2)))

            camera_shake.x = random.randint(-intensity, intensity)
            camera_shake.y = random.randint(-intensity, intensity)

            self.camera_shake_frames -= 1 * dt
            
        return pygame.Vector2(self.box.x, self.box.y) - self.box_dimensions + camera_shake
        