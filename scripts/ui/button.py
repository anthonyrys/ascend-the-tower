from scripts.tools.bezier import presets, get_bezier_point
from scripts.tools import create_outline_edge

from scripts.ui.frame import Frame

import pygame
import os

class Button(Frame):
    def __init__(self, position, img, strata, alpha=None):
        super().__init__(position, img, None, strata, alpha)
        self.sprite_id = 'button'

        self.on_select = None

        self.hover_info = {
            'color': (255, 255, 255)
        }

        self.bezier_info['inherited'] = False

    def on_hover_start(self, scene):
        if self.flag is not None:
            return

        self.hovering = True

    def on_hover_end(self, scene):
        if self.flag is not None:
            return

        self.hovering = False

    def on_mouse_down(self, scene, event):
        if not self.hovering:
            return

        if event != 1:
            return

        if self.flag is not None:
            return

        self.on_hover_end(scene)
        self.on_select[0](*self.on_select[1])

    def set_flag(self, flag):
        self.flag = flag

    def display(self, scene, dt):
        if self.bezier_info['x']['f'][0] < self.bezier_info['x']['f'][1]:
            x_info = self.bezier_info['x']
            self.rect.x = x_info['p_0'] + (x_info['p_1'] - x_info['p_0']) * get_bezier_point(x_info['f'][0] / x_info['f'][1], *x_info['b'])

            self.bezier_info['x']['f'][0] += 1 * dt

        if self.bezier_info['y']['f'][0] < self.bezier_info['y']['f'][1]:
            y_info = self.bezier_info['y']
            self.rect.y = y_info['p_0'] + (y_info['p_1'] - y_info['p_0']) * get_bezier_point(y_info['f'][0] / y_info['f'][1], *y_info['b'])

            self.bezier_info['y']['f'][0] += 1 * dt

        if self.bezier_info['alpha']['f'][0] < self.bezier_info['alpha']['f'][1]:
            alpha_info = self.bezier_info['alpha']
            alpha = alpha_info['a_0'] + (alpha_info['a_1'] - alpha_info['a_0']) * get_bezier_point(alpha_info['f'][0] / alpha_info['f'][1], *alpha_info['b'])

            self.image.set_alpha(alpha)

            self.bezier_info['alpha']['f'][0] += 1 * dt

        if self.hovering:
            create_outline_edge(self, self.hover_info['color'], scene.ui_surface, 3)

        super().display(scene, dt)
