from scripts.prefabs.entity import Entity

from scripts.utils.bezier import presets, get_bezier_point
import pygame

class Particle(Entity):
    def __init__(self, position, img, dimensions, strata, alpha=None):
        super().__init__(position, img, dimensions, strata, alpha)
        self.sprite_id = 'particle'

        self.goal_info = {}
        self.beziers = {
            'position': presets['ease_out']
        }
        
        self.frames = [0, 0]
        self.gravity = None

    def display(self, scene, dt):
        super().display(scene, dt)

    def set_goal(self, frames, **info):
        frames = 1 if frames <= 0 else frames
        self.frames[1] = frames

        for k, v in info.items():
            self.goal_info[k] = v

    def set_beziers(self, **beziers):
        for info, bezier in beziers.items():
            self.beziers[info] = bezier

    def set_gravity(self, gravity):
        self.gravity = gravity

class Circle(Particle):
    def __init__(self, position, color, radius, width, attach=None):
        super().__init__(position, (0, 0, 0), (radius * 2, radius * 2), None)
        self.secondary_sprite_id = 'circle'

        self.alpha = self.image.get_alpha()
        self.radius = [radius, radius]
        self.width = [width, width]
        self.x = [position[0], position[0]]
        self.y = [position[1], position[1]]

        self.color = color
        self.attach = attach

        self.set_beziers(
            radius=presets['ease_out'],
            width=[*presets['rest'], 0],
            alpha=[*presets['rest'], 0]
        )

    def display(self, scene, dt):
        if self.frames[0] > self.frames[1]:
            scene.del_sprites(self)
            return

        abs_prog = self.frames[0] / self.frames[1]

        self.radius[1] = self.radius[0] + ((self.goal_info['radius'] - self.radius[0]) * get_bezier_point(abs_prog, *self.beziers['radius']))

        if 'width' in self.goal_info:
            self.width[1] = self.width[0] + round((self.goal_info['width'] - self.width[0]) * get_bezier_point(abs_prog, *self.beziers['width']))

        self.image = pygame.transform.scale(self.image, (self.radius[1] * 2, self.radius[1] * 2))
        self.image.set_colorkey((0, 0, 0))
        self.image.fill((0, 0, 0))

        if self.attach:
            self.rect = self.image.get_rect(center=(self.attach.rect.center))
            
        elif 'position' in self.goal_info:
            self.rect = self.image.get_rect(center=(
                self.x[0] + (self.goal_info['position'][0] - self.x[0]) * get_bezier_point(abs_prog, *self.beziers['position']),
                self.y[0] + (self.goal_info['position'][1] - self.y[0]) * get_bezier_point(abs_prog, *self.beziers['position']))
            )
        
        else:
            self.rect = self.image.get_rect(center=(self.x[0], self.y[0]))

        if self.gravity:
            self.rect.y += self.gravity * self.frames[0]

        pygame.draw.circle(
            self.image,
            self.color, (self.image.get_width() * .5, self.image.get_height() * .5), self.radius[1], self.width[1]
        )

        if 'alpha' in self.goal_info:
            self.image.set_alpha(self.alpha + ((self.goal_info['alpha'] - self.alpha) * get_bezier_point(abs_prog, *self.beziers['alpha'])))

        super().display(scene, dt)
        self.frames[0] += 1 * dt

class Image(Particle):
    def __init__(self, position, img, strata, alpha):
        super().__init__(position, img, None, strata, alpha)
        self.secondary_sprite_id = 'image'

        self.alpha = self.image.get_alpha()

        self.x = [position[0], position[0]]
        self.y = [position[1], position[1]]
        
        self.set_beziers(
            alpha=[*presets['rest'], 0],
            dimensions=presets['ease_out']
        )

    def display(self, scene, dt):
        if self.frames[0] > self.frames[1]:
            scene.del_sprites(self)
            return

        abs_prog = self.frames[0] / self.frames[1]

        if 'dimensions' in self.goal_info:
            self.image = pygame.transform.scale(
                self.original_image,
                (self.original_image.get_width() + ((self.goal_info['dimensions'][0] - self.original_image.get_width()) * get_bezier_point(abs_prog, *self.beziers['dimensions'])),
                self.original_image.get_height() + ((self.goal_info['dimensions'][1] - self.original_image.get_height()) * get_bezier_point(abs_prog, *self.beziers['dimensions'])))
            )

        if 'position' in self.goal_info:
            pos = [
                self.x[0] + (self.goal_info['position'][0] - self.x[0]) * get_bezier_point(abs_prog, *self.beziers['position']),
                self.y[0] + (self.goal_info['position'][1] - self.y[0]) * get_bezier_point(abs_prog, *self.beziers['position'])
            ]

            self.rect = self.image.get_rect(center = pos)

        else:
            self.rect = self.image.get_rect(center = [self.x[0], self.y[0]])

        if 'alpha' in self.goal_info:
            self.image.set_alpha(self.alpha + ((self.goal_info['alpha'] - self.alpha) * get_bezier_point(abs_prog, *self.beziers['alpha'])))

        super().display(scene, dt)
        self.frames[0] += 1 * dt
