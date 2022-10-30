from src.engine import Entity

class Tile(Entity):
    def __init__(self, position, img, dimensions, strata=...):
        super().__init__(position, img, dimensions, strata)

    def display(self, scene, dt):
        scene.entity_surface.blit(self.image, self.rect)