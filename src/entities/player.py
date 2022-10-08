from src.constants import (
    GRAVITY, 
    MAX_GRAVITY,
    COLORS,
    COLOR_VALUES,
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
        self.rect_offset = pygame.Vector2(self.image.get_width() / 2, 0)

        self.per_frame_movespeed = 4
        self.max_movespeed = 12
        self.direction = 0
        
        self.jump_power = 24
        self.jump = 0
        self.max_jump = 2

        self.ability_properties = {
            'dash_range': 60
        }

        self.states = {
            'facing': 0,
            'dead': False
        }

        self.collide_points = {
            'top': False, 
            'bottom': False, 
            'left': False, 
            'right': False
        }

        self.event_timers = { 
            'jump': 8,
            'color_swap': 25,
            'respawn': 75
        }
        
        self.events = {
            'jump': 0,
            'color_swap': 0,
            'dead': 0
        }

        self.color = COLORS[0]
        self.prev_color = self.color

    def on_death(self, scene):
        self.states['dead'] = True
        self.image.set_alpha(0)

        scene.camera.set_camera_shake(60)

        pos = pygame.Vector2(self.rect.centerx, self.rect.centery)
        particles = list()
        for _ in range(40):
            particles.append(
                Circle(
                    Circle.Info(pos + pygame.Vector2(random.randint(-750, 750), random.randint(-750, 750)), 80, radius=0, width=0),
                    pos, pygame.Color(255, 255, 255), 15, 0, self.strata + 1
                )
            )

        scene.add_sprites(particles)

        self.events['dead'] = scene.frames

    def on_respawn(self, scene):
        self.rect.center = self.spawn_location
        self.image.set_alpha(255)

        self.jump = 0
        self.velocity = pygame.Vector2()

        self.states['dead'] = False

    def on_jump(self, scene, dt):
        if not (scene.frames - self.events['jump']) * dt >= self.event_timers['jump']:
            return

        if self.jump > 0:
            self.velocity.y = -(self.jump_power)

            self.jump -= 1
            self.events['jump'] = scene.frames

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

    def apply_movement(self, scene, keys, dt):
        if self.velocity.x > self.max_movespeed:
            self.velocity.x -= (self.per_frame_movespeed)

        elif self.velocity.x < -(self.max_movespeed):
            self.velocity.x += (self.per_frame_movespeed)

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity.x += (self.per_frame_movespeed) if self.velocity.x < self.max_movespeed else 0
        
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
           self.velocity.x -= (self.per_frame_movespeed) if self.velocity.x > -(self.max_movespeed) else 0

        if not keys[pygame.K_d] and not keys[pygame.K_a] and not keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            if self.velocity.x > 0:
                self.velocity.x -= (self.per_frame_movespeed)

            elif self.velocity.x < 0:
                self.velocity.x += (self.per_frame_movespeed)

        if keys[pygame.K_w] or keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            self.on_jump(scene, dt)

    def apply_gravity(self, dt):
        if not self.collide_points['bottom']:
            self.velocity.y += GRAVITY * dt if self.velocity.y < MAX_GRAVITY * dt else 0

        else:
            self.velocity.y = GRAVITY * dt

    def apply_collision_x(self, scene):
        if self.states.get('dead'):
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

            if self.color != barrier.color:
                continue

            right_x = barrier.rect.centerx + (barrier.image.get_width() / 2)
            left_x = barrier.rect.centerx - (barrier.image.get_width() / 2)

            if self.rect.centerx - barrier.rect.centerx < 0:
                if (self.rect.left) > left_x:
                    self.on_death(scene)
                    return

                else:
                    self.rect.right = barrier.rect.left
                    self.collide_points['right'] = True

                    self.velocity.x = 0

            elif self.rect.centerx - barrier.rect.centerx > 0:
                if (self.rect.right) < right_x:
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
        if self.states.get('dead'):
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

            if self.color != barrier.color:
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

    def set_color(self, frames, keys, dt):
        if self.states.get('dead'):
            return

        if not (frames - self.events['color_swap']) * dt >= self.event_timers['color_swap']:
            return

        if keys[pygame.K_e]:
            if COLORS.index(self.color) + 1 == len(COLORS):
                self.color = COLORS[0]
            else:
                self.color = COLORS[COLORS.index(self.color) + 1]

            self.events['color_swap'] = frames

        elif keys[pygame.K_q]:
            if COLORS.index(self.color) == 0:
                self.color = COLORS[-1]
            else:
                self.color = COLORS[COLORS.index(self.color) - 1]

            self.events['color_swap'] = frames

    def set_keyframe_state(self):
        if self.states.get('dead'):
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

    def set_image(self, scene, dt):
        if self.states.get('dead'):
            return

        self.image = self.keyframes.iterate_frame(dt)

        if self.states['facing'] < 0:
            self.image = pygame.transform.flip(self.image, True, False).convert_alpha()

        else:
            self.image = pygame.transform.flip(self.image, False, False).convert_alpha()

        if self.color != self.prev_color:
            pos = pygame.Vector2(self.rect.centerx, self.rect.centery)
            particles = list()

            particles.append(
                Circle(
                    Circle.Info(pos, 27, radius=150, width=1),
                    pos, 
                    COLOR_VALUES[self.color],
                    5,
                    15,
                    self.strata + 1
                )
            )
            scene.add_sprites(particles)

        self.image = self.mask.to_surface(
            setcolor=COLOR_VALUES[self.color], 
            unsetcolor=pygame.Color(0, 0, 0, 0)
        )

        self.prev_color = self.color

    def display(self, scene, dt):
        if self.states.get('dead'):
            if (scene.frames - self.events['dead']) * dt > self.event_timers['respawn']:
                self.on_respawn(scene)

        else:
            keys = pygame.key.get_pressed()

            self.apply_gravity(dt)
            self.apply_movement(scene, keys, dt)

            self.rect.x += self.velocity.x * dt
            self.apply_collision_x(scene)

            if abs(self.velocity.y * dt) < 1 and dt != 0:
                self.velocity.y = 1 / dt

            self.rect.y += self.velocity.y * dt
            self.apply_collision_y(scene)
            
            if self.velocity.x > 0:
                self.states['facing'] = 1

            elif self.velocity.x < 0:
                self.states['facing'] = -1

            self.set_keyframe_state()
            self.set_color(scene.frames, keys, dt)
            self.set_image(scene, dt)

        scene.sprite_surface.blit(
            self.image, 
            (self.rect.x - self.rect_offset.x, self.rect.y - self.rect_offset.y, 0, 0),
        )
        