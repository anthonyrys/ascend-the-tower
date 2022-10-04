from src.constants import (
    GRAVITY, 
    MAX_GRAVITY,
    COLORS,
    COLOR_VALUES,
    SCREEN_DIMENSIONS
)
from src.entities.entity import Entity, Tags
from src.entities.particle import Circle
from src.misc.keyframes import PlayerFrames

import pygame
import random

class Player(Entity):
    def __init__(self, position, strata=...):
        super().__init__(position, pygame.Surface((32, 64)), ..., strata)

        self.add_tags(Tags.PLAYER)
        self.keyframes = PlayerFrames()

        self.spawn_location = position

        self.per_frame_movespeed = 4
        self.max_movespeed = 12
        self.direction = 0

        self.jump_power = 24
        self.jump = 0
        self.max_jump = 2

        self.rect_offset = pygame.Vector2(self.image.get_width() / 2, 0)
        self.collide_points = {
            'top': False, 
            'bottom': False, 
            'left': False, 
            'right': False
        }

        self.cooldowns = { 
            'jump': 8,
            'color_swap': 25,
        }

        self.last_frames = {
            'jump': 0,
            'color_swap': 0,
        }

        self.dead = False
        self.death_time = 0
        self.respawn_timer = 50 

        self.color = COLORS[0]
        self.prev_color = self.color

    def on_death(self, scene):
        self.dead = True
        self.image.set_alpha(0)

        scene.camera.set_camera_shake(35)

        pos = pygame.Vector2(self.rect.centerx, self.rect.centery)
        particles = list()
        for _ in range(40):
            particles.append(
                Circle(
                    Circle.Info(pos + pygame.Vector2(random.randint(-500, 500), random.randint(-500, 500)), 40, radius=0, width=0),
                    pos, pygame.Color(255, 255, 255), 15, 0, self.strata + 1
                )
            )

        scene.add_sprites(particles)

        self.death_time = scene.frames

    def on_respawn(self, scene):
        self.image.set_alpha(255)
        self.rect.center = self.spawn_location

        self.jump = 0
        self.velocity = pygame.Vector2()

        self.dead = False

    def apply_movement(self, scene):
        frames = scene.frames
        keys = pygame.key.get_pressed()

        if self.velocity.x > self.max_movespeed:
            self.velocity.x -= self.per_frame_movespeed

        elif self.velocity.x < -(self.max_movespeed):
            self.velocity.x += self.per_frame_movespeed

        if keys[pygame.K_d]:
            self.velocity.x += self.per_frame_movespeed if self.velocity.x < self.max_movespeed else 0
        
        if keys[pygame.K_a]:
           self.velocity.x -= self.per_frame_movespeed if self.velocity.x > -(self.max_movespeed) else 0

        if not keys[pygame.K_d] and not keys[pygame.K_a]:
            if self.velocity.x > 0:
                self.velocity.x -= self.per_frame_movespeed

            elif self.velocity.x < 0:
                self.velocity.x += self.per_frame_movespeed

        if keys[pygame.K_w] or keys[pygame.K_SPACE]:
            if frames - self.last_frames['jump'] >= self.cooldowns['jump']:
                if self.jump > 0:
                    self.velocity.y = -(self.jump_power)

                    self.jump -= 1
                    self.last_frames['jump'] = frames

                    pos = pygame.Vector2(self.rect.centerx, self.rect.centery) + pygame.Vector2(0, 20)

                    particles = list()
                    particles.append(
                        Circle(
                            Circle.Info(pos + pygame.Vector2(-40, 10), 15, radius=0, width=0),
                            pos, pygame.Color(255, 255, 255), 6, 0, self.strata + 1
                        )
                    )

                    particles.append(
                        Circle(
                            Circle.Info(pos + pygame.Vector2(40, 10), 15, radius=0, width=0),
                            pos, pygame.Color(255, 255, 255), 6, 0, self.strata + 1
                        )
                    )


                    scene.add_sprites(particles)

    def apply_gravity(self):
        if not self.collide_points['bottom']:
            self.velocity.y += GRAVITY if self.velocity.y < MAX_GRAVITY else 0

        else:
            self.velocity.y = GRAVITY

    def apply_collision_x(self, scene):
        if self.dead:
            return

        self.collide_points['right'] = False
        self.collide_points['left'] = False

        collidables = [s for s in scene.sprites if s.get_tag(Tags.COLLIDABLE)]
        for collidable in collidables:
            if not self.rect.colliderect(collidable.rect):
                continue

            if self.velocity.x > 0:
                self.rect.right = collidable.rect.left
                self.collide_points['right'] = True

                self.velocity.x = 0

            if self.velocity.x < 0:
                self.rect.left = collidable.rect.right
                self.collide_points['left'] = True
                
                self.velocity.x = 0

        barriers = [s for s in scene.sprites if s.get_tag(Tags.BARRIER)]
        for barrier in barriers:
            if not self.rect.colliderect(barrier.rect):
                continue

            if self.color == barrier.color:
                continue

            right_x = barrier.rect.centerx + (barrier.image.get_width() / 2)
            left_x = barrier.rect.centerx - (barrier.image.get_width() / 2)

            if self.rect.centerx - barrier.rect.centerx < 0:
                if self.rect.centerx > left_x:
                    self.on_death(scene)
                    return

                else:
                    self.rect.right = barrier.rect.left
                    self.collide_points['right'] = True

                    self.velocity.x = 0

            elif self.rect.centerx - barrier.rect.centerx > 0:
                if self.rect.centerx < right_x:
                    self.on_death(scene)
                    return

                else:
                    self.rect.left = barrier.rect.right
                    self.collide_points['left'] = True

                    self.velocity.x = 0
                    
            else:
                self.on_death(scene)
                return

    def apply_collision_y(self, scene):
        if self.dead:
            return

        self.collide_points['top'] = False
        self.collide_points['bottom'] = False

        collidables = [s for s in scene.sprites if s.get_tag(Tags.COLLIDABLE)]
        for collidable in collidables:
            if not self.rect.colliderect(collidable.rect):
                continue

            if self.velocity.y > 0:
                self.rect.bottom = collidable.rect.top
                self.collide_points['bottom'] = True

                if self.jump != self.max_jump:
                    self.jump = self.max_jump
                    
                self.velocity.y = 0

            if self.velocity.y < 0:
                self.rect.top = collidable.rect.bottom
                self.collide_points['top'] = True

                self.velocity.y = 0

        barriers = [s for s in scene.sprites if s.get_tag(Tags.BARRIER)]
        for barrier in barriers:
            if not self.rect.colliderect(barrier.rect):
                continue

            if self.color == barrier.color:
                continue

            if self.velocity.y > 0:
                self.rect.bottom = barrier.rect.top
                self.collide_points['bottom'] = True

                if self.jump != self.max_jump:
                    self.jump = self.max_jump
                        
                self.velocity.y = 0

            if self.velocity.y < 0:
                self.rect.top = barrier.rect.bottom
                self.collide_points['top'] = True

                self.velocity.y = 0

    def set_color(self, frames):
        if self.dead:
            return

        keys = pygame.key.get_pressed()

        if not frames - self.last_frames['color_swap'] >= self.cooldowns['color_swap']:
            return

        if keys[pygame.K_e]:
            if COLORS.index(self.color) + 1 == len(COLORS):
                self.color = COLORS[0]
            else:
                self.color = COLORS[COLORS.index(self.color) + 1]

            self.last_frames['color_swap'] = frames

        elif keys[pygame.K_q]:
            if COLORS.index(self.color) == 0:
                self.color = COLORS[-1]
            else:
                self.color = COLORS[COLORS.index(self.color) - 1]

            self.last_frames['color_swap'] = frames

    def set_state(self):
        if self.dead:
            return

        if not self.collide_points['bottom']:
            if self.velocity.y < 0:
                self.keyframes.state = 'jump'
            else:
                self.keyframes.state = 'fall'

        elif self.velocity.x > 0 or self.velocity.x < 0:
            self.keyframes.state = 'run'

        else:
            self.keyframes.state = 'idle'

    def set_image(self, scene):
        if self.dead:
            return

        self.set_state()
        self.image = self.keyframes.iterate_frame()

        if self.direction < 0:
            self.image = pygame.transform.flip(self.image, True, False).convert_alpha()

        else:
            self.image = pygame.transform.flip(self.image, False, False).convert_alpha()

        w, h = self.image.get_size()
        for x in range(w):
            for y in range(h):
                if self.image.get_at((x, y)) != pygame.Color(255, 255, 255):
                    continue

                self.image.set_at((x, y), COLOR_VALUES[self.color])
 
        if self.color != self.prev_color:
            pos = pygame.Vector2(self.rect.centerx, self.rect.centery)
            particles = list()

            particles.append(
                Circle(
                    Circle.Info(pos, 23, radius=150, width=1),
                    pos, 
                    COLOR_VALUES[self.color],
                    5,
                    15,
                    self.strata + 1
                )
            )
            scene.add_sprites(particles)

        self.prev_color = self.color

    def display(self, scene):
        if self.dead:
            if scene.frames - self.death_time > self.respawn_timer:
                self.on_respawn(scene)

        else:
            self.apply_gravity()
            self.apply_movement(scene)

            self.rect.x += (self.velocity.x)
            self.apply_collision_x(scene)

            self.rect.y += self.velocity.y 
            self.apply_collision_y(scene)

            if self.velocity.x > 0:
                self.direction = 1

            elif self.velocity.x < 0:
                self.direction = -1

            self.set_color(scene.frames)
            self.set_image(scene)

        scene.sprite_surface.blit(
            self.image, 
            (self.rect.x - self.rect_offset.x, self.rect.y - self.rect_offset.y, 0, 0),
        )
        