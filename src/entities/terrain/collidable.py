from src.entities.entity import Entity, Tags

import pygame

class Collidable(Entity):
    def __init__(self, position, img, dimensions):
        super().__init__(position, img, dimensions, 2)
        
        self.add_tags(Tags.COLLIDABLE)
        
    def display(self, display_surface):
        display_surface.blit(self.image, self.rect)
