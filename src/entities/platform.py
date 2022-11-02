from src.engine import Entity

class Platform(Entity):
    def __init__(self, position, img, dimensions, strata=None):
        super().__init__(position, img, dimensions, strata)

    def display(self, scene, dt):
        scene.entity_surface.blit(self.image, self.rect)
