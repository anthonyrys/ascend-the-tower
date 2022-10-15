import pygame

class Mouse(pygame.sprite.Sprite):
    def __init__(self):
        self.image = pygame.Surface(pygame.Vector2(5, 5)).convert_alpha()
        self.image.fill(pygame.Color(255, 255, 255, 255))
        self.image.set_colorkey(pygame.Color(0, 0, 0))

        self.rect = self.image.get_rect()

    @property
    def mask(self):
        return pygame.mask.from_surface(self.image)

    def display(self, scene):
        self.rect.center = pygame.mouse.get_pos()
        scene.ui_surface.blit(self.image, self.rect)
