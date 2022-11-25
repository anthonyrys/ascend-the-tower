from src.engine import Entity

class Tile(Entity):
    def __init__(self, position, img, dimensions, strata=None):
        super().__init__(position, img, dimensions, strata)

    def display(self, scene, dt):
        super().display(scene, dt)
