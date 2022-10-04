from src.entities.entity import Entity, Tags

import pygame
import math

class Outline(Entity):
    class Info():
        def __init__(self, dimensions, speed, size):
            if speed == 0: 
                speed = 1

            self.dimensions = dimensions
            self.size = size

            self.speed = speed

    def __init__(self, info, position, color, size, img, strata):
        super().__init__(position, img, ..., strata)

        self.add_tags(Tags.PARTICLE)

        self.base_dimensions = pygame.Vector2(self.image.get_width(), self.image.get_height())
        self.dimensions = self.base_dimensions
        self.base_size, self.size = size, size
        self.position = position

        self.color = color
        self.info = info
        self.frame_count = 0

    def display(self, scene):
        if self.frame_count != self.info.speed:
            abs_prog = self.frame_count / self.info.speed

            self.image = pygame.transform.scale(
                self.image, 
                pygame.Vector2(
                    self.base_dimensions.x + round(((self.info.dimensions.x - self.base_dimensions.x) * ((1 - math.pow(1 - abs_prog, 3))))),
                    self.base_dimensions.y +  round(((self.info.dimensions.y - self.base_dimensions.y) * ((1 - math.pow(1 - abs_prog, 3)))))
                )
            )
            
            self.size = self.base_size + round((self.info.size - self.base_size) * (abs_prog * abs_prog * abs_prog * abs_prog))
            self.rect.x = self.position.x - self.image.get_width() / 2
            self.rect.y = self.position.y - self.image.get_height() / 2

            outline = self.mask.outline()
            for i, pixel in enumerate(outline):
                outline[i] = (pixel[0] + self.rect.x, pixel[1] + self.rect.y)

            pygame.draw.polygon(scene.sprite_surface, self.color, outline, self.size)

            self.frame_count += 1

        else:
            scene.del_sprites(self)

class Circle(Entity):
    class Info():
        def __init__(self, position, speed, radius=..., width=...):
            if speed == 0: 
                speed = 1

            self.position = position
            self.radius = radius
            self.width = width

            self.speed = speed

    def __init__(self, info, position, color, radius, width, strata):
        super().__init__(position, pygame.Color(0, 0, 0, 0), pygame.Vector2(info.radius * 2, info.radius * 2), strata)

        self.add_tags(Tags.PARTICLE)

        self.fill = pygame.Color(0, 0, 0)

        self.position, self.base_position = position, position
        self.radius, self.base_radius = radius, radius
        self.width, self.base_width = width, width

        self.color = color
        self.info = info
        self.frame_count = 0

    def display(self, scene):
        if self.frame_count != self.info.speed:
            abs_prog = self.frame_count / self.info.speed

            self.rect.center = self.base_position + pygame.Vector2(
                (self.info.position.x - self.base_position.x) * (1 - pow(1 - abs_prog, 4)),
                (self.info.position.y - self.base_position.y) * (1 - pow(1 - abs_prog, 4)),
            )

            if self.info.radius != ...:
                self.radius = self.base_radius + ((self.info.radius - self.base_radius) * ((1 - math.pow(1 - abs_prog, 3))))

            if self.info.width != ...:
                self.width = self.base_width + round((self.info.width - self.base_width) * (1 - math.cos((abs_prog * math.pi) / 2)))

            pygame.draw.circle(
                scene.sprite_surface, 
                self.color, self.rect.center, self.radius, self.width
            )

            self.frame_count += 1

        else:
            scene.del_sprites(self)
