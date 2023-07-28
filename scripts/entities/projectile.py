from scripts import ENEMY_COLOR

from scripts.visual_fx.particle import Image
from scripts.entities.entity import Entity

from scripts.tools import check_pixel_collision, check_line_collision, get_distance

import pygame

class Projectile(Entity):
    def __init__(self, position, img, dimensions, strata, info, alpha=None, velocity=[0, 0], duration=0, settings={}):
        if isinstance(img, tuple):
            self.radius = dimensions
            self.color = img

            surf = pygame.Surface((dimensions * 2, dimensions * 2)).convert_alpha()
            surf.set_colorkey((0, 0, 0))

            if 'player' in settings:
                pygame.draw.circle(surf, (255, 255, 255), surf.get_rect().center, dimensions)
            else:
                pygame.draw.circle(surf, ENEMY_COLOR, surf.get_rect().center, dimensions)

            pygame.draw.circle(surf, img, surf.get_rect().center, dimensions * .75)

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

        self.prev_player_position = scene.player.rect.center
        self.duration -= 1 * dt

        if 'afterimages' in self.settings:
            self.apply_afterimages(scene, dt)

        if 'display' in self.settings:
            self.settings['display'](self, scene, dt)

        super().display(scene, dt)

class ProjectileStandard(Projectile):
    def __init__(self, position, img, dimensions, strata, info, alpha=None, velocity=[0, 0], duration=0, settings={}):
        super().__init__(position, img, dimensions, strata, info, alpha, velocity, duration, settings)

        self.secondary_sprite_id = 'standard_projectile'

    def display(self, scene, dt):
        if self.info:
            if self.info['collision'] == 'pixel':
                for sprite in scene.get_sprites(self.info['collisions']):
                    if get_distance(self, sprite) > 100:
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
                    if get_distance(self, sprite) > 100:
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
