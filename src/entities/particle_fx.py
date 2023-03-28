from src.engine import Easings, Entity, SpriteMethods

from src.core_systems.level_handler import Level

import pygame
import math
import os

class Particle(Entity):
    def __init__(self, position, img, dimensions, strata, alpha=None):
        super().__init__(position, img, dimensions, strata, alpha)

        self.goal_info = {}
        self.easing_styles = {
            'position': getattr(Easings, 'custom_position_particle_fx')
        }
        
        self.frame_count = 0
        self.frame_count_max = 0

        self.gravity = None

    def display(self, scene, dt):
        super().display(scene, dt)

    def set_goal(self, frame_count_max, **info):
        frame_count_max = 1 if frame_count_max <= 0 else frame_count_max
        self.frame_count_max = frame_count_max

        for k, v in info.items():
            self.goal_info[k] = v

    def set_easings(self, **easings):
        for info, style in easings.items():
            if info not in self.goal_info.keys():
                continue
        
            if not hasattr(Easings, style):
                continue

            self.easing_styles[info] = getattr(Easings, style)

    def set_gravity(self, gravity):
        self.gravity = gravity

class Circle(Particle):
    def __init__(self, position, color, radius, width):
        super().__init__(position, (0, 0, 0), (radius * 2, radius * 2), None)

        self.position, self.base_position = position, position
        self.radius, self.base_radius = radius, radius
        self.width, self.base_width = width, width

        self.color = color

        self.easing_styles['radius'] = getattr(Easings, 'ease_out_cubic')
        self.easing_styles['width'] = getattr(Easings, 'ease_in_sine')

    def display(self, scene, dt):
        if self.frame_count > self.frame_count_max:
            scene.del_sprites(self)
            return

        abs_prog = self.frame_count / self.frame_count_max

        self.rect.center = (
            self.base_position[0] + (self.goal_info['position'][0] - self.base_position[0]) * self.easing_styles['position'](abs_prog),
            self.base_position[1] + (self.goal_info['position'][1] - self.base_position[1]) * self.easing_styles['position'](abs_prog),
        )

        if self.gravity:
            self.rect.y += self.gravity * self.frame_count

        self.radius = self.base_radius + ((self.goal_info['radius'] - self.base_radius) * self.easing_styles['radius'](abs_prog))
        self.width = self.base_width + round((self.goal_info['width'] - self.base_width) * self.easing_styles['width'](abs_prog))

        self.image.fill((0, 0, 0))
        pygame.draw.circle(
            self.image,
            self.color, (self.image.get_width() * .5, self.image.get_height() * .5), self.radius, self.width
        )

        super().display(scene, dt)
        self.frame_count += 1 * dt

class Image(Particle):
    def __init__(self, position, img, strata, alpha, target=None):
        super().__init__(position, img, None, strata, alpha)
        
        self.alpha = self.image.get_alpha()
        self.position, self.original_position = position, position

        self.target = target

        self.easing_styles['alpha'] = getattr(Easings, 'ease_in_sine')
        self.easing_styles['dimensions'] = getattr(Easings, 'ease_out_quint')

    def display(self, scene, dt):
        if self.frame_count > self.frame_count_max:
            scene.del_sprites(self)
            return

        abs_prog = self.frame_count / self.frame_count_max

        self.image = pygame.transform.scale(
            self.original_image,
            (self.original_image.get_width() + ((self.goal_info['dimensions'][0] - self.original_image.get_width()) * self.easing_styles['dimensions'](abs_prog)),
            self.original_image.get_height() + ((self.goal_info['dimensions'][1] - self.original_image.get_height()) * self.easing_styles['dimensions'](abs_prog)))
        )

        if self.target is None:
            self.rect = self.image.get_rect(center = self.original_position)
        else:
            self.rect = self.image.get_rect(center = (
                self.target.center_position[0] - self.target.rect_offset[0],
                self.target.center_position[1] - self.target.rect_offset[1]
                )
            )

        self.image.set_alpha(self.alpha + ((self.goal_info['alpha'] - self.alpha) * self.easing_styles['alpha'](abs_prog)))

        super().display(scene, dt)
        self.frame_count += 1 * dt

class Experience(Particle):
    def __init__(self, position, color, radius, width, amount):
        super().__init__(position, (0, 0, 0), (radius * 2, radius * 2), None)

        self.position, self.base_position = position, position
        self.radius = radius
        self.width = width

        self.color = color
        self.amount = amount

        self.ms = [2, 6]
        self.ms_distance = 100

    def display(self, scene, dt):
        dist = SpriteMethods.get_distance(self, scene.player)
        
        if dist <= self.ms_distance * .5:
            scene.del_sprites(self)
            Level.register_experience(scene, self.amount)
            return

        self.glow['size'] = abs(round(math.sin(self.frame_count * .04), 2)) + 1
        if self.frame_count > self.frame_count_max:
            if dist <= self.ms_distance:
                if self.rect.x < scene.player.rect.x:
                    self.velocity[0] += self.ms[0] if self.velocity[0] < self.ms[1] else 0
                elif self.rect.x > scene.player.rect.x:
                    self.velocity[0] -= self.ms[0] if self.velocity[0] > -self.ms[1] else 0

                if self.rect.y <= scene.player.rect.y:
                    self.velocity[1] += self.ms[0] if self.velocity[1] < self.ms[1] else 0
                elif self.rect.y > scene.player.rect.y:
                    self.velocity[1] -= self.ms[0] if self.velocity[1] > -self.ms[1] else 0

            else:
                if self.velocity[0] > 0:
                    self.velocity[0] -= self.ms[0] * .25
                elif self.velocity[0] < 0:
                    self.velocity[0] += self.ms[0] * .25

                if self.velocity[1] > 0:
                    self.velocity[1] -= self.ms[0] * .25
                elif self.velocity[1] < 0:
                    self.velocity[1] += self.ms[0] * .25

            self.rect.x += round(self.velocity[0] * dt)
            self.rect.y += round(self.velocity[1] * dt)

            self.frame_count += 1 * dt
            super().display(scene, dt)
            return

        abs_prog = self.frame_count / self.frame_count_max

        self.rect.center = (
            self.base_position[0] + (self.goal_info['position'][0] - self.base_position[0]) * self.easing_styles['position'](abs_prog),
            self.base_position[1] + (self.goal_info['position'][1] - self.base_position[1]) * self.easing_styles['position'](abs_prog),
        )

        self.image.fill((0, 0, 0))
        pygame.draw.circle(
            self.image,
            self.color, (self.image.get_width() * .5, self.image.get_height() * .5), self.radius, self.width
        )

        super().display(scene, dt)
        self.frame_count += 1 * dt