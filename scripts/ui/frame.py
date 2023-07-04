from scripts.utils.sprite import Sprite

import pygame

class Frame(Sprite):
    def __init__(self, position, img, dimensions, strata, alpha=None):
        super().__init__(position, img, dimensions, strata, alpha)

        self.uses_entity_surface = False
        
        self.hovering = False
        self.pressed = False
        
        self.hover_rect = pygame.Rect(self.rect.x, self.rect.y, 0, 0)

        self.global_offset = (0, 0)

    def display(self, scene, dt):    
        super().display(scene, dt)

        if self.uses_entity_surface:
            scene.entity_surface.blit(
                self.image, 
                (self.rect.x + self.global_offset[0], self.rect.y + self.global_offset[1]),
            )
            
        else:
            scene.ui_surface.blit(
                self.image, 
                (self.rect.x + self.global_offset[0], self.rect.y + self.global_offset[1]),
            )

    def on_del_sprite(self, scene, time):
        self.delay_timers.append([time, lambda: scene.del_sprites(self), []])
        
    def on_hover_start(self, scene):
        ...

    def on_hover_end(self, scene):
        ...

    def on_press(self, scene):
        ...

