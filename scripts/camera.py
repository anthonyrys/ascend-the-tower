from scripts import SCREEN_DIMENSIONS

from scripts.tools.bezier import presets, get_bezier_point

import pygame
import random

class CameraTemplate:
    def __init__(self, focus):
        self.focus = focus
        self.offset = [0, 0]
        self.zoom = 1

        self.camera_shake_info = {
            'frames': 0,
            'max_frames': 0,
            'intensity': 10
        }

        self.camera_tween_info = {
            'frames': 0,
            'max_frames': 0,
            'start_pos': None
        }

    def set_camera_shake(self, frames, intensity=10):
        self.camera_shake_info['frames'] = frames
        self.camera_shake_info['max_frames'] = frames
        self.camera_shake_info['intensity'] = intensity

    def set_camera_tween(self, frames):
        self.camera_tween_info['frames'] = 0
        self.camera_tween_info['max_frames'] = frames
        self.camera_tween_info['start_pos'] = self.offset

class BoxCamera(CameraTemplate):
    def __init__(self, focus):
        super().__init__(focus)

        self.box_dimensions = (555, 265)
        self.box = pygame.Rect(
            self.box_dimensions[0],
            self.box_dimensions[1],

            SCREEN_DIMENSIONS[0] - (self.box_dimensions[0] * 2),
            SCREEN_DIMENSIONS[1] - (self.box_dimensions[1] * 2)
        )

    def update(self, dt):
        camera_shake = [0, 0]
        if self.camera_shake_info['frames'] > 0:
            abs_prog = self.camera_shake_info['frames'] / self.camera_shake_info['max_frames']
            intensity = round((self.camera_shake_info['intensity']) * get_bezier_point(abs_prog, *presets['rest'], 0))

            camera_shake[0] = random.randint(-intensity, intensity)
            camera_shake[1] = random.randint(-intensity, intensity)

            self.camera_shake_info['frames'] -= 1 * dt

        if self.focus.rect.left < self.box.left:
            self.box.left = self.focus.rect.left

        elif self.focus.rect.right > self.box.right:
            self.box.right = self.focus.rect.right

        if self.focus.rect.bottom > self.box.bottom:
            self.box.bottom = self.focus.rect.bottom

        elif self.focus.rect.top < self.box.top:
            self.box.top = self.focus.rect.top
            
        offset = [
            self.box[0] - self.box_dimensions[0] + camera_shake[0], 
            self.box[1] - self.box_dimensions[1] + camera_shake[1]
        ]

        if self.camera_tween_info['frames'] < self.camera_tween_info['max_frames']:
            abs_prog = self.camera_tween_info['frames'] / self.camera_tween_info['max_frames']

            tweened_offset = [
                self.camera_tween_info['start_pos'][0] + ((offset[0] - self.camera_tween_info['start_pos'][0]) * get_bezier_point(abs_prog, *presets['ease_out'])),
                self.camera_tween_info['start_pos'][1] + ((offset[1] - self.camera_tween_info['start_pos'][1]) * get_bezier_point(abs_prog, *presets['ease_out']))
            ]

            self.camera_tween_info['frames'] += 1 * dt

            self.offset = tweened_offset
            return tweened_offset

        else:
            self.offset = offset
            return offset