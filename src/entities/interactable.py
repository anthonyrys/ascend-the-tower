from src.entities.entity import Entity, Tags

import pygame

class Interactable(Entity):
    def __init__(self, position, img, dimensions, strata, indp=False, dist=15):
        super().__init__(position, img, dimensions, strata)
        
        self.add_tags(Tags.INTERACTABLE)

        self.independent = indp
        self.interact_dist = dist

        self.selected = False
        self.interacting = False
        self.interacter = None
        
    # <overridden by child classes>
    def display(self, scene, dt):
        ...

    # <overridden by child classes>
    def on_select(self):
        ...

    # <overridden by child classes>
    def on_interact(self):
        ...

    # <overridden by child classes>
    def on_release(self):
        ...

    # <overridden by child classes>
    def apply_interact_effect(self, interacter):
        ...