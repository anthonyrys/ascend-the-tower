'''
Holds the projectile baseclass as well as subclasses.
'''

from scripts.engine import Easings, Entity, check_pixel_collision, check_line_collision, get_distance

from scripts.entities.particle_fx import Image

import pygame

class Projectile(Entity):
    '''
    The projectile baseclass; intended to be inherited from.

    Variables:
        info: general information about the projectile.
        trail: whether or not the projectile leaves a trail.
        afterimages: whether or not the projectile will leave afterimages.

        duration: duration of the projectile.
        prev_positions: list of the previous positions the projectile had.
        prev_player_position: previous position of the player.

        alpha_info: information on how the image alpha should be tweened.

    Methods:
        on_collision(): called when the projectile collides with its given sprites.
        set_alpha_tween(): sets the alpha_info values.
    '''

    def __init__(self, position, img, dimensions, strata, info, alpha=None, velocity=[0, 0], trail=False, afterimages=False):
        if isinstance(img, tuple):
            self.radius = dimensions
            self.color = img

            surf = pygame.Surface((dimensions * 2, dimensions * 2)).convert_alpha()
            surf.set_colorkey((0, 0, 0))
            pygame.draw.circle(surf, img, surf.get_rect().center, dimensions)

            img = surf
            dimensions = None

        super().__init__(position, img, dimensions, strata, alpha)

        self.sprite_id = 'projectile'
        
        self.velocity = velocity
        self.info = info
        self.trail = trail
        self.afterimages = afterimages

        self.duration = 0
        self.prev_positions = []
        self.prev_player_position = None

        self.alpha_info = {
            'easing_style': getattr(Easings, 'ease_out_quint'),

            'frames': 0,
            'max_frames': 0,

            'alpha': 0,
            'base_alpha': 0
        }

    def on_collision(self, scene, sprite):
        if 'collision_function' in self.info:
            if sprite.sprite_id in self.info['collision_function']:
                self.info['collision_function'][sprite.sprite_id](scene, self, sprite)

            elif 'default' in self.info['collision_function']:
                self.info['collision_function']['default'](scene, self, sprite)

        scene.del_sprites(self)

    def set_alpha_tween(self, frames, alpha):
        self.alpha_info['frames'] = 0
        self.alpha_info['max_frames'] = frames

        self.alpha_info['alpha'] = alpha
        self.alpha_info['base_alpha'] = self.image.get_alpha()

    def display(self, scene, dt):
        if self.alpha_info['frames'] < self.alpha_info['max_frames']:
            abs_prog = self.alpha_info['frames'] / self.alpha_info['max_frames']
            alpha = self.alpha_info['base_alpha'] + ((self.alpha_info['alpha'] - self.alpha_info['base_alpha']) * self.alpha_info['easing_style'](abs_prog))

            self.image.set_alpha(alpha)
            self.alpha_info['frames'] += 1 * dt

        super().display(scene, dt)

class ProjectileStandard(Projectile):
    def __init__(self, position, img, dimensions, strata, info, alpha=None, velocity=[0, 0], trail=False, afterimages=False):
        super().__init__(position, img, dimensions, strata, info, alpha, velocity, trail, afterimages)

        self.secondary_sprite_id = 'standard_projectile'

    def display(self, scene, dt):
        if self.duration >= self.info['duration']:
            scene.del_sprites(self)
            return
        
        self.prev_positions.append([self.rect.x, self.rect.y])

        self.rect.x += round(self.velocity[0] * dt, 1)
        self.rect.y += round(self.velocity[1] * dt, 1)

        if self.info:
            if self.info['collision'] == 'pixel':
                for sprite in [s for s in scene.sprites if s.sprite_id not in self.info['collision_exclude']]:
                    if get_distance(self, sprite) > 100:
                        continue

                    if sprite.sprite_id == 'player' and self.prev_player_position:
                        if check_line_collision(self.prev_player_position, scene.player.rect.center, [self]):
                            self.on_collision(scene, sprite)

                    if not check_pixel_collision(self, sprite):
                        continue

                    self.on_collision(scene, sprite)

            if self.info['collision'] == 'rect':
                for sprite in [s for s in scene.sprites if s.sprite_id not in self.info['collision_exclude']]:
                    if get_distance(self, sprite) > 100:
                        continue

                    if sprite.sprite_id == 'player' and self.prev_player_position:
                        if check_line_collision(self.prev_player_position, scene.player.rect.center, [self]):
                            self.on_collision(scene, sprite)

                    if not self.rect.colliderect(sprite.rect):
                        continue

                    self.on_collision(scene, sprite)

        if self.trail:
            for i in range(self.radius):
                cir_pos = [
                    self.rect.centerx - (round(self.velocity[0]) * (.25 * (i + 1))),
                    self.rect.centery - (round(self.velocity[1]) * (.25 * (i + 1)))
                ]

                pygame.draw.circle(scene.entity_surface, self.color, cir_pos, (self.radius - (i + 1)))

        self.prev_player_position = scene.player.rect.center
        self.duration += 1 * dt

        super().display(scene, dt)