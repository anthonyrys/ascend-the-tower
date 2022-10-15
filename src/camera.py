from src.constants import SCREEN_DIMENSIONS

import pygame
import random
import math
        
class BoxCamera():
    def __init__(self, focus):
        self.focus = focus
        self.offset = pygame.Vector2()

        self.box_dimensions = pygame.Vector2(555, 265)
        self.box = pygame.Rect(
            self.box_dimensions.x,
            self.box_dimensions.y,

            SCREEN_DIMENSIONS.x - (self.box_dimensions.x * 2),
            SCREEN_DIMENSIONS.y - (self.box_dimensions.y * 2)
        )

        self.camera_shake_frames_max, self.camera_shake_frames = 0, 0
        self.camera_shake_intensity = 10

        self.camera_tween_frames_max, self.camera_tween_frames = 0, 0
        self.start_pos = None

    def set_camera_shake(self, frames):
        self.camera_shake_frames_max = frames
        self.camera_shake_frames = frames

    def set_camera_tween(self, frames):
        self.camera_tween_frames_max = frames
        self.camera_tween_frames = 0
        self.start_pos = pygame.Vector2(self.box.x, self.box.y) - self.box_dimensions

    def update(self, dt):
        camera_shake = pygame.Vector2()
        if self.camera_shake_frames > 0:
            abs_prog = self.camera_shake_frames / self.camera_shake_frames_max
            intensity = round((self.camera_shake_intensity) * (1 - math.cos((abs_prog * math.pi) / 2)))

            camera_shake.x = random.randint(-intensity, intensity)
            camera_shake.y = random.randint(-intensity, intensity)

            self.camera_shake_frames -= 1 * dt

        if self.focus.rect.left < self.box.left:
            self.box.left = self.focus.rect.left

        elif self.focus.rect.right > self.box.right:
            self.box.right = self.focus.rect.right

        if self.focus.rect.bottom > self.box.bottom:
            self.box.bottom = self.focus.rect.bottom

        elif self.focus.rect.top < self.box.top:
            self.box.top = self.focus.rect.top
        
        offset = pygame.Vector2(self.box.x, self.box.y) - self.box_dimensions + camera_shake

        if self.camera_tween_frames < self.camera_tween_frames_max:
            abs_prog = self.camera_tween_frames / self.camera_tween_frames_max

            tweened_offset = self.start_pos + pygame.Vector2(
                (offset.x - self.start_pos.x) * (1 - math.pow(1 - abs_prog, 5)),
                (offset.y - self.start_pos.y) * (1 - math.pow(1 - abs_prog, 5)),
            )

            self.camera_tween_frames += 1 * dt

            self.offset = tweened_offset
            return tweened_offset

        else:
            self.offset = offset
            return offset
        