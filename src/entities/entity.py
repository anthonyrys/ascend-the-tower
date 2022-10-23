from enum import Enum, auto
import pygame

class Tags(Enum):
    PLAYER = auto()
    PARTICLE = auto()
    COLLIDABLE  = auto()
    INTERACTABLE = auto()
    BARRIER = auto()

class Entity(pygame.sprite.Sprite):
    def __init__(self, position, img, dimensions, strata, alpha=...):
        pygame.sprite.Sprite.__init__(self)
        self.active = True
        self.strata = strata

        if isinstance(img, pygame.Color):
            self.image = pygame.Surface(dimensions).convert_alpha()
            self.image.set_colorkey(pygame.Color(0, 0, 0))
            
            self.image.fill(img)

        else:
            self.image = img

        self.original_image = self.image

        if alpha != ...:
            self.image.set_alpha(alpha)

        self.tags = list()

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position
        
        self.original_rect = self.rect

        self.collide_points = {
            'top': False, 
            'bottom': False, 
            'left': False, 
            'right': False
        }

        self.collision_ignore = list()

        self.velocity = pygame.Vector2()
        self.outline = False

    @property
    def mask(self):
        return pygame.mask.from_surface(self.image)

    # <overridden by child classes>
    def display(self, scene, dt):
        ...
        
    def get_tag(self, tag):
        return tag in self.tags

    def add_tags(self, tags, *args):
        if not isinstance(tags, list):
            tags = list([tags])
        
        for arg in args: 
            tags.append(arg)

        for tag in tags:
            self.tags.append(tag)

    def remove_tags(self, tags, *args):
        if not isinstance(tags, list):
            tags = list([tags])
        
        for arg in args: 
            tags.append(arg)

        for tag in tags:
            if not tag in self.tags:
                continue

            self.tags.remove(tag)
