from src.engine import Entity

import pygame

class Collidable(Entity):
    def __init__(self, position, img, dimensions):
        super().__init__(position, img, dimensions, 2)

    # <overridden by child classes>
    def display(self, scene, dt):
        scene.entity_surface.blit(self.image, self.rect)
    
    # <overridden by child classes>
    def on_collide(self):
        ...