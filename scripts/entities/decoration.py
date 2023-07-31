from scripts.entities.entity import Entity

import pygame
import inspect
import sys

def get_all_decoration():
    decoration_list = [t for t in inspect.getmembers(sys.modules[__name__], inspect.isclass)]
			
    return decoration_list

class Decoration(Entity):
    def __init__(self, position, img, dimensions, strata=None, alpha=None):
        super().__init__(position, img, dimensions, strata, alpha)
        self.sprite_id = 'decoration'

    def display(self, scene, dt):
        super().display(scene, dt)
