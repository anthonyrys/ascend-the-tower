from src.engine import Easings, Entity

import pygame

class Particle(Entity):
    class Info():
        def __init__(self, speed, **info):
            speed = 1 if speed == 0 else speed
            self.speed = speed

            self.info = {}
            for k, v in info.items():
                self.info[k] = v
            
    def __init__(self, info_class, position, img, dimensions, strata, alpha=None):
        super().__init__(position, img, dimensions, strata, alpha)

        self.info = info_class.info
        self.speed = info_class.speed
        self.frame_count = 0

    def display(self, scene, dt):
        super().display(scene, dt)

class Circle(Particle):
    def __init__(self, info_class, position, color, radius, width):
        super().__init__(info_class, position, (0, 0, 0), (radius * 2, radius * 2), None)

        self.position, self.base_position = position, position
        self.radius, self.base_radius = radius, radius
        self.width, self.base_width = width, width

        self.color = color

    def display(self, scene, dt):
        if self.frame_count > self.speed:
            scene.del_sprites(self)
            return

        abs_prog = self.frame_count / self.speed

        self.rect.center = (
            self.base_position[0] + (self.info['position'][0] - self.base_position[0]) * (1 - pow(1 - abs_prog, 4)),
            self.base_position[1] + (self.info['position'][1] - self.base_position[1]) * (1 - pow(1 - abs_prog, 4)),
        )

        self.radius = self.base_radius + ((self.info['radius'] - self.base_radius) * Easings.ease_out_cubic(abs_prog))
        self.width = self.base_width + round((self.info['width'] - self.base_width) * Easings.ease_in_sine(abs_prog))

        self.image.fill((0, 0, 0))
        pygame.draw.circle(
            self.image,
            self.color, (self.image.get_width() * .5, self.image.get_height() * .5), self.radius, self.width
        )

        super().display(scene, dt)
        self.frame_count += 1 * dt

class Image(Particle):
    def __init__(self, info_class, position, img, strata, alpha):
        super().__init__(info_class, position, img, None, strata, alpha)

        self.alpha = self.image.get_alpha()

    def display(self, scene, dt):
        if self.frame_count > self.speed:
            scene.del_sprites(self)
            return

        abs_prog = self.frame_count / self.speed

        self.image.set_alpha(self.alpha + ((self.info['alpha'] - self.alpha) * Easings.ease_out_sine(abs_prog)))

        super().display(scene, dt)
        self.frame_count += 1 * dt