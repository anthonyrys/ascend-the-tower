from scripts.utils.sprite import Sprite

class Entity(Sprite):
    def __init__(self, position, img, dimensions, strata, alpha=None):
        super().__init__(position, img, dimensions, strata, alpha)

        self.uses_ui_surface = False

        self.velocity = [0, 0]

    def display(self, scene, dt):
        super().display(scene, dt)

        if self.uses_ui_surface:
            scene.ui_surface.blit(
                self.image, 
                (self.rect.x - self.rect_offset[0], self.rect.y - self.rect_offset[1]),
            )
            
        else:
            scene.entity_surface.blit(
                self.image, 
                (self.rect.x - self.rect_offset[0], self.rect.y - self.rect_offset[1]),
            )