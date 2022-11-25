from src.engine import Easings, Entity

import pygame

class Particle(Entity):
    class Info():
        def __init__(self, speed, **info):
            speed = 1 if speed == 0 else speed
            self.speed = speed

            self.info = dict()
            for k, v in info.items():
                self.info[k] = v
            
    def __init__(self, info_class, position, img, dimensions, strata, alpha=None):
        super().__init__(position, img, dimensions, strata, alpha)

        self.info = info_class.info
        self.speed = info_class.speed
        self.frame_count = 0

    # <overridden by child classes>
    def display(self, scene, dt):
        ...

class Outline(Particle):
    def __init__(self, info_class, position, color, size, img):
        super().__init__(info_class, position, img, None, None)

        self.base_dimensions = self.image.get_size()
        self.dimensions = self.base_dimensions
        self.base_size, self.size = size, size
        self.position = position
        self.color = color

    def display(self, scene, dt):
        if scene.paused:
            outline = self.mask.outline()
            for i, pixel in enumerate(outline):
                outline[i] = (pixel[0] + self.rect.x, pixel[1] + self.rect.y)

            pygame.draw.polygon(scene.entity_surface, self.color, outline, self.size)
            return

        if self.frame_count > self.speed:
            scene.del_sprites(self)
            return

        abs_prog = self.frame_count / self.speed

        tween_size_x = round(((self.info['dimensions'][0] - self.base_dimensions[0]) * Easings.ease_out_cubic(abs_prog)))
        tween_size_y = round(((self.info['dimensions'][1] - self.base_dimensions[1]) * Easings.ease_out_cubic(abs_prog)))

        self.image = pygame.transform.scale(
            self.image, (
                self.base_dimensions[0] + tween_size_x,
                self.base_dimensions[1] + tween_size_y
            )
        )
            
        self.size = self.base_size + round((self.info['size'] - self.base_size) * Easings.ease_in_quint(abs_prog))

        self.rect.x = self.position[0] - (tween_size_x / 2)
        self.rect.y = self.position[1] - (tween_size_y / 2)

        outline = self.mask.outline()
        for i, pixel in enumerate(outline):
            outline[i] = (pixel[0] + self.rect.x, pixel[1] + self.rect.y)

        pygame.draw.polygon(scene.entity_surface, self.color, outline, self.size)

        self.frame_count += 1 * dt

class Circle(Particle):
    def __init__(self, info_class, position, color, radius, width):
        super().__init__(info_class, position, (0, 0, 0, 0), (radius * 2, radius * 2), None)

        self.position, self.base_position = position, position
        self.radius, self.base_radius = radius, radius
        self.width, self.base_width = width, width

        self.color = color

    def display(self, scene, dt):
        if scene.paused:
            pygame.draw.circle(
                scene.entity_surface, 
                self.color, self.rect.center, self.radius, self.width
            )

            return

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

        pygame.draw.circle(
            scene.entity_surface, 
            self.color, self.rect.center, self.radius, self.width
        )

        self.frame_count += 1 * dt

class Image(Particle):
    def __init__(self, info_class, position, color, dimensions, alpha):
        super().__init__(info_class, position, color, dimensions, None, alpha)

        self.base_position = position
        self.base_alpha = alpha

    def display(self, scene, dt):
        if scene.paused:
            scene.entity_surface.blit(self.image, self.rect)
            return

        if self.frame_count > self.speed:
            scene.del_sprites(self)
            return

        abs_prog = self.frame_count / self.speed

        self.image.set_alpha(self.base_alpha + ((self.info['alpha'] - self.base_alpha) * Easings.ease_out_cubic(abs_prog)))

        self.frame_count += 1 * dt
        scene.entity_surface.blit(self.image, self.rect)
