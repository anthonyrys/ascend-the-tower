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
        settings: settings for how the projectile should be displayed.

        duration: duration of the projectile.
        prev_positions: list of the previous positions the projectile had.
        prev_player_position: previous position of the player.

    Methods:
        on_collision(): called when the projectile collides with its given sprites.
        apply_afterimages(): applies afterimages of the projectile if enabled.
    '''

    def __init__(self, position, img, dimensions, strata, info, alpha=None, velocity=[0, 0], duration=0, settings={}):
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
        self.settings = settings

        self.duration = duration
        self.prev_positions = []
        self.prev_player_position = None

    def on_collision(self, scene, sprite):
        if 'collision_function' in self.info:
            if sprite.sprite_id in self.info['collision_function']:
                self.info['collision_function'][sprite.sprite_id](scene, self, sprite)

            elif 'default' in self.info['collision_function']:
                self.info['collision_function']['default'](scene, self, sprite)

        scene.del_sprites(self)

    def apply_afterimages(self, scene, dt):
        self.settings['afterimages'][0] += 1 * dt
        if self.settings['afterimages'][0] < self.settings['afterimages'][1]:
            return
        
        self.settings['afterimages'][0] = 0
        
        img = Image(
            self.center_position,
            self.image.copy(), self.strata - 1, 50
        )
        
        img.set_goal(5, alpha=0, dimensions=self.image.get_size())

        scene.add_sprites(img)

    def display(self, scene, dt):
        if self.duration <= 0:
            scene.del_sprites(self)
            return

        self.rect.x += round(self.velocity[0] * dt, 1)
        self.rect.y += round(self.velocity[1] * dt, 1)

        if 'trail' in self.settings:
            for i in range(self.radius):
                cir_pos = [
                    self.rect.centerx - (round(self.velocity[0]) * (.25 * (i + 1))),
                    self.rect.centery - (round(self.velocity[1]) * (.25 * (i + 1)))
                ]

                pygame.draw.circle(scene.entity_surface, self.color, cir_pos, (self.radius - (i + 1)))

        self.prev_player_position = scene.player.rect.center
        self.duration -= 1 * dt

        if 'afterimages' in self.settings:
            self.apply_afterimages(scene, dt)

        super().display(scene, dt)

class ProjectileStandard(Projectile):
    def __init__(self, position, img, dimensions, strata, info, alpha=None, velocity=[0, 0], duration=0, settings={}):
        super().__init__(position, img, dimensions, strata, info, alpha, velocity, duration, settings)

        self.secondary_sprite_id = 'standard_projectile'

    def display(self, scene, dt):
        if self.info:
            if self.info['collision'] == 'pixel':
                for sprite in scene.get_sprites(self.info['collisions']):
                    if get_distance(self, sprite) > 100 and sprite.secondary_sprite_id != 'floor':
                        continue

                    if sprite.sprite_id == 'player' and self.prev_player_position:
                        if check_line_collision(self.prev_player_position, scene.player.rect.center, [self]):
                            self.on_collision(scene, sprite)
                            break

                    if not check_pixel_collision(self, sprite):
                        continue

                    self.on_collision(scene, sprite)
                    break

            if self.info['collision'] == 'rect':
                for sprite in scene.get_sprites(self.info['collisions']):
                    if get_distance(self, sprite) > 100 and sprite.secondary_sprite_id != 'floor':
                        continue

                    if sprite.sprite_id == 'player' and self.prev_player_position:
                        if check_line_collision(self.prev_player_position, scene.player.rect.center, [self]):
                            self.on_collision(scene, sprite)
                            break

                    if not self.rect.colliderect(sprite.rect):
                        continue

                    self.on_collision(scene, sprite)
                    break

        super().display(scene, dt)
