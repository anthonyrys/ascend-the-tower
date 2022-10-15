from src.entities.entity import Entity, Tags

import pygame

class Interactable(Entity):
    def __init__(self, position, img, dimensions, strata):
        super().__init__(position, img, dimensions, strata)
        
        self.add_tags(Tags.INTERACTABLE)

        self.interacting = False
        self.interacter = None
        
    # <overridden by child classes>
    def display(self, scene):
        ...

    # <overridden by child classes>
    def on_interact(self):
        ...