from src.constants import (
    GRAVITY, 
    MAX_GRAVITY,
    COLORS,
    COLOR_VALUES
)

from src.entities.entity import Entity, Tags
from src.entities.particle_fx import Circle, Image

from src.frame_iterator import PlayerFrames
from src.sprite_methods import Methods

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

        self.keybinds = {
            'left': [pygame.K_a, pygame.K_LEFT],
            'right': [pygame.K_d, pygame.K_RIGHT],
            'jump': [pygame.K_w, pygame.K_SPACE, pygame.K_UP],

            'ability': pygame.K_f,
            'color_forward': pygame.K_e,
            'color_backward': pygame.K_q
        }

        self.pressed = dict()
        for keybind in self.keybinds.keys():
            self.pressed[keybind] = False

        self.interact_obj = None

        self.states = {
            'dead': False,
            'interacting': False
        }

        self.ability_data = {
            0: {},
            1: {},
            2: {
                'timer': 80,
                'range': 40
            }
        }

        self.color = COLORS[0]
        self.prev_color = self.color

        self.event_timers = { 
            'color_swap': 25,
            'ability_2': self.ability_data[2]['timer'],
            'jump': 8,
            'respawn': 75
        }
        
        self.events = dict()
        for event in self.event_timers.keys():
            self.events[event] = 0

        self.collision_ignore = list()

    def get_keys_pressed(self):
        keys = pygame.key.get_pressed()

        for action in self.pressed.keys():
            self.pressed[action] = False

            if not isinstance(self.keybinds[action], list):
                self.pressed[action] = keys[self.keybinds[action]]
                continue

            for val in self.keybinds[action]:
                if not keys[val]:
                    continue

                self.pressed[action] = keys[val]
                break

    def on_mouse_down(self, scene):
        if self.states['dead']:
            return

        self.on_interact_start(scene)
        
    def on_mouse_up(self, scene):
        self.on_interact_end()

    def on_interact_start(self, scene):
        interactable = scene.get_selected()
        if not interactable:
            return

        if not interactable.on_interact(self):
            return

        self.interact_obj = interactable
        self.states['interacting'] = True

    def on_interact_end(self):
        if not self.states['interacting']:
            return
        
        if self.interact_obj.independent:
            return

        self.states['interacting'] = False

        self.interact_obj.on_release()
        self.interact_obj = None

    def on_death(self, scene):
        self.on_interact_end()

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

        particles.append(
            Circle(
                Circle.Info(pos, 45, radius=250, width=1),
                pos, 
                pygame.Color(255, 255, 255),
                5,
                15,
                self.strata + 1
            )
        )
        scene.add_sprites(particles)

        self.events['respawn'] = scene.frames

    def on_respawn(self, scene):
        scene.camera.set_camera_tween(55)
        self.rect.center = self.spawn_location

        self.jump = 0
        self.velocity = pygame.Vector2()

        self.states['dead'] = False
        self.image.set_alpha(255)

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

    def on_ability(self, scene, dt):
        if self.color == COLORS[0]:
            ...

        elif self.color == COLORS[1]:
            ...

        elif self.color == COLORS[2]:       
            if not (scene.frames - self.events['ability_2']) * dt >= self.event_timers['ability_2']:
                return

            if self.velocity == pygame.Vector2():
                return

            start_pos = pygame.Vector2(self.rect.centerx, self.rect.centery)

            xs = [-self.max_movespeed, 0, self.max_movespeed]
            ys = [-self.jump_power / 4, 0]


            end_pos = pygame.Vector2(
                min(xs, key = lambda v: abs(v - self.velocity.x)),
                min(ys, key = lambda v: abs(v - self.velocity.y))
            )

            if end_pos == pygame.Vector2():
                return

            self.events['ability_2'] = scene.frames

            end_pos = start_pos + pygame.Vector2(
                min(xs, key = lambda v: abs(v - self.velocity.x)),
                min(ys, key = lambda v: abs(v - self.velocity.y))
            ) * self.ability_data[2]['range']

            col_sprites = [s for s in scene.sprites if s.get_tag(Tags.COLLIDABLE)]
            for barrier in [s for s in scene.sprites if s.get_tag(Tags.BARRIER)]:
                if self.color != barrier.color:
                    continue

                col_sprites.append(barrier)

            clipped_sprites = Methods.check_line_collision(start_pos, end_pos, col_sprites)
            if clipped_sprites:
                clip_sprite = Methods.get_closest_sprite(self, clipped_sprites)
                clipline = clip_sprite.rect.clipline(start_pos, end_pos)

                end_pos = pygame.Vector2(clipline[0][0], clipline[0][1])

            if end_pos.x - start_pos.x < 0:
                end_pos.x += self.image.get_width()
            elif end_pos.x - start_pos.x > 0:
                end_pos.x -= self.image.get_width()

            if end_pos.y - start_pos.y < 0:
                end_pos.y += self.image.get_height()
            elif end_pos.y - start_pos.y > 0:
                end_pos.y -= self.image.get_height()

            self.rect.center = end_pos
            self.velocity.y = 0 if self.velocity.y > 0 else self.velocity.y

            particles = list()
            offset = pygame.Vector2(self.image.get_size()[0] / 2, self.image.get_size()[1] / 2)
            
            particles.append(
                Image(
                    Image.Info(start_pos - offset, 50, 0),
                    start_pos - offset, self.image.copy(), ..., 75, self.strata
                )
            )

            for _ in range(15):
                particles.append(
                    Circle(
                        Circle.Info(
                            (end_pos + pygame.Vector2(random.randint(-250, 250), random.randint(-250, 250))) + self.velocity * 25, 
                            100, radius=0, width=0),
                        end_pos, COLOR_VALUES[self.color], 10, 0, self.strata + 1
                    )
                )

            scene.add_sprites(particles)
            scene.camera.set_camera_tween(25)
            
    def apply_movement(self, scene, dt):
        if self.velocity.x > self.max_movespeed:
            self.velocity.x -= (self.per_frame_movespeed)

        elif self.velocity.x < -(self.max_movespeed):
            self.velocity.x += (self.per_frame_movespeed)

        if self.pressed['right']:
            self.velocity.x += (self.per_frame_movespeed) if self.velocity.x < self.max_movespeed else 0
        
        if self.pressed['left']:
           self.velocity.x -= (self.per_frame_movespeed) if self.velocity.x > -(self.max_movespeed) else 0

        if not self.pressed['right'] and not self.pressed['left']:
            if self.velocity.x > 0:
                self.velocity.x -= (self.per_frame_movespeed)

            elif self.velocity.x < 0:
                self.velocity.x += (self.per_frame_movespeed)

        if self.pressed['jump']:
            self.on_jump(scene, dt)

    def apply_gravity(self, dt):
        if not self.collide_points['bottom']:
            self.velocity.y += GRAVITY * dt if self.velocity.y < MAX_GRAVITY * dt else 0

        else:
            self.velocity.y = GRAVITY * dt

    def apply_collision_x(self, scene):
        self.collide_points['right'] = False
        self.collide_points['left'] = False

        collidables = [s for s in scene.sprites if s.get_tag(Tags.COLLIDABLE)]
        for collidable in collidables:
            if not self.rect.colliderect(collidable.rect):
                if collidable in self.collision_ignore:
                    self.collision_ignore.remove(collidable)
                
                continue

            if collidable in self.collision_ignore:
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
                if barrier in self.collision_ignore:
                    self.collision_ignore.remove(barrier)
                
                continue

            if barrier in self.collision_ignore:
                continue

            if self.color != barrier.color:
                continue

            if self.rect.centerx - barrier.rect.centerx < 0:
                if self.rect.left > barrier.rect.midleft[0]:
                    if self.rect.centery - barrier.rect.centery < 0:
                        if (self.rect.top >= barrier.rect.top):
                            return True

                        else:
                            self.collision_ignore.append(barrier)
                            self.velocity.y = -15

                    if self.rect.centery - barrier.rect.centery > 0:
                        if (self.rect.bottom <= barrier.rect.bottom):
                            return True

                        else:
                            self.collision_ignore.append(barrier)
                            self.velocity.y = 15

                else:
                    if abs(self.rect.right - barrier.rect.left) > 12:
                        self.collision_ignore.append(barrier)
                        self.velocity.x = -28
                    
                    else:
                        self.rect.right = barrier.rect.left
                        self.collide_points['right'] = True

                        self.velocity.x = 0

            elif self.rect.centerx - barrier.rect.centerx > 0:
                if self.rect.right < barrier.rect.midright[0]:
                    if self.rect.centery - barrier.rect.centery < 0:
                        if (self.rect.top >= barrier.rect.top):
                            return True

                        else:
                            self.collision_ignore.append(barrier)
                            self.velocity.y = -15

                    if self.rect.centery - barrier.rect.centery > 0:
                        if (self.rect.bottom <= barrier.rect.bottom): 
                            return True

                        else:
                            self.collision_ignore.append(barrier)
                            self.velocity.y = 15

                else:
                    if abs(self.rect.left - barrier.rect.right) > 12:
                        self.collision_ignore.append(barrier)
                        self.velocity.x = 28
                    
                    else:
                        self.rect.left = barrier.rect.right
                        self.collide_points['left'] = True
                        
                        self.velocity.x = 0
                    
            else:
                return True

    def apply_collision_y(self, scene):
        self.collide_points['top'] = False
        self.collide_points['bottom'] = False

        collidables = [s for s in scene.sprites if s.get_tag(Tags.COLLIDABLE)]
        for collidable in collidables:
            if not self.rect.colliderect(collidable.rect):
                if collidable in self.collision_ignore:
                    self.collision_ignore.remove(collidable)
                
                continue

            if collidable in self.collision_ignore:
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
                if barrier in self.collision_ignore:
                    self.collision_ignore.remove(barrier)
                
                continue

            if barrier in self.collision_ignore:
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

    def set_color(self, scene, dt):
        frames = scene.frames

        if not (frames - self.events['color_swap']) * dt >= self.event_timers['color_swap']:
            return

        if self.pressed['color_forward']:
            if COLORS.index(self.color) + 1 == len(COLORS):
                self.color = COLORS[0]
            else:
                self.color = COLORS[COLORS.index(self.color) + 1]

            self.events['color_swap'] = frames

        elif self.pressed['color_backward']:
            if COLORS.index(self.color) == 0:
                self.color = COLORS[-1]
            else:
                self.color = COLORS[COLORS.index(self.color) - 1]

            self.events['color_swap'] = frames

    def set_frame_state(self):
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
        if self.velocity.x > 0:
            self.direction = 1

        elif self.velocity.x < 0:
            self.direction = -1

        if self.keyframes.state == 'run':
            self.image = self.keyframes.iterate(dt, abs(self.velocity.x / self.max_movespeed))

        else:
            self.image = self.keyframes.iterate(dt, 1)

        self.image = pygame.transform.flip(self.image, True, False).convert_alpha() if self.direction < 0 else self.image

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
        if self.states['dead']:
            if (scene.frames - self.events['respawn']) * dt > self.event_timers['respawn']:
                self.on_respawn(scene)

        else:
            self.get_keys_pressed()

            self.apply_gravity(dt)
            self.apply_movement(scene, dt)

            if self.pressed['ability']:
                self.on_ability(scene, dt)

            self.rect.x += self.velocity.x * dt
            if (self.apply_collision_x(scene)):
                self.on_death(scene)
                scene.entity_surface.blit(
                    self.image, 
                    (self.rect.x - self.rect_offset.x, self.rect.y - self.rect_offset.y, 0, 0),
                )
                
                return
            
            if self.interact_obj:
                self.interact_obj.apply_interact_effect(self)

            self.rect.y += self.velocity.y * dt
            self.apply_collision_y(scene)

            self.set_frame_state()
            self.set_color(scene, dt)
            self.set_image(scene, dt)

        scene.entity_surface.blit(
            self.image, 
            (self.rect.x - self.rect_offset.x, self.rect.y - self.rect_offset.y, 0, 0),
        )
        