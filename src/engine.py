from src.constants import (
    GRAVITY, 
    MAX_GRAVITY,
    SCREEN_DIMENSIONS
)

import pygame
import random
import math

class Easings():
    @staticmethod
    def ease_in_sine(abs_prog):
        return 1 - math.cos((abs_prog * math.pi) / 2)

    @staticmethod
    def ease_in_cubic(abs_prog):
        return abs_prog * abs_prog * abs_prog

    @staticmethod
    def ease_in_quint(abs_prog):
        return abs_prog * abs_prog * abs_prog * abs_prog

    @staticmethod
    def ease_in_cir(abs_prog):
        return 1 - math.sqrt(1 - math.pow(abs_prog, 2))


    @staticmethod
    def ease_out_sine(abs_prog):
        return math.sin((abs_prog * math.PI) / 2)

    @staticmethod
    def ease_out_cubic(abs_prog):
        return 1 - math.pow(1 - abs_prog, 3)

    @staticmethod
    def ease_out_quint(abs_prog):
        return 1 - math.pow(1 - abs_prog, 5)

    @staticmethod
    def ease_out_cir(abs_prog):
        return math.sqrt(1 - math.pow(abs_prog - 1, 2))

class Camera():
    class Box():
        def __init__(self, focus):
            self.focus = focus
            self.offset = pygame.Vector2()

            self.box_dimensions = pygame.Vector2(555, 265)
            self.box = pygame.Rect(
                self.box_dimensions.x,
                self.box_dimensions.y,

                SCREEN_DIMENSIONS.x - (self.box_dimensions.x * 2),
                SCREEN_DIMENSIONS.y - (self.box_dimensions.y * 2)
            )

            self.camera_shake_frames_max, self.camera_shake_frames = 0, 0
            self.camera_shake_intensity = 10

            self.camera_tween_frames_max, self.camera_tween_frames = 0, 0
            self.start_pos = None

        def set_camera_shake(self, frames):
            self.camera_shake_frames_max = frames
            self.camera_shake_frames = frames

        def set_camera_tween(self, frames):
            self.camera_tween_frames_max = frames
            self.camera_tween_frames = 0
            self.start_pos = pygame.Vector2(self.box.topleft) - self.box_dimensions

        def update(self, dt):
            camera_shake = pygame.Vector2()
            if self.camera_shake_frames > 0:
                abs_prog = self.camera_shake_frames / self.camera_shake_frames_max
                intensity = round((self.camera_shake_intensity) * Easings.ease_in_sine(abs_prog))

                camera_shake.x = random.randint(-intensity, intensity)
                camera_shake.y = random.randint(-intensity, intensity)

                self.camera_shake_frames -= 1 * dt

            if self.focus.rect.left < self.box.left:
                self.box.left = self.focus.rect.left

            elif self.focus.rect.right > self.box.right:
                self.box.right = self.focus.rect.right

            if self.focus.rect.bottom > self.box.bottom:
                self.box.bottom = self.focus.rect.bottom

            elif self.focus.rect.top < self.box.top:
                self.box.top = self.focus.rect.top
            
            offset = pygame.Vector2(self.box.x, self.box.y) - self.box_dimensions + camera_shake

            if self.camera_tween_frames < self.camera_tween_frames_max:
                abs_prog = self.camera_tween_frames / self.camera_tween_frames_max

                tweened_offset = self.start_pos + pygame.Vector2(
                    (offset.x - self.start_pos.x) * Easings.ease_out_quint(abs_prog),
                    (offset.y - self.start_pos.y) * Easings.ease_out_quint(abs_prog),
                )

                self.camera_tween_frames += 1 * dt

                self.offset = tweened_offset
                return tweened_offset

            else:
                self.offset = offset
                return offset

class Entity(pygame.sprite.Sprite):
    def __init__(self, position, img, dimensions, strata, alpha=None):
        pygame.sprite.Sprite.__init__(self)
        self.active = True
        self.strata = strata

        if isinstance(img, pygame.Color):
            self.image = pygame.Surface(dimensions).convert_alpha()
            self.image.set_colorkey(pygame.Color(0, 0, 0))
            
            self.image.fill(img)

        else:
            self.image = img

        self.original_image = self.image

        if alpha:
            self.image.set_alpha(alpha)

        self.rect = self.image.get_bounding_rect()
        self.rect.x, self.rect.y = position
        
        self.original_rect = self.rect

        self.collide_points = {
            'top': False, 
            'bottom': False, 
            'left': False, 
            'right': False
        }

        self.collisions = list()
        self.collision_ignore = list()

        self.velocity = pygame.Vector2()

    @property
    def mask(self):
        return pygame.mask.from_surface(self.image)

    # <overridden by child classes>
    def display(self, scene, dt):
        ...

    def apply_collision_x_default(self, collidables):
        callback_collision = list()

        for collidable in collidables:
            if not self.rect.colliderect(collidable.rect):
                if collidable in self.collision_ignore:
                    self.collision_ignore.remove(collidable)
                
                if collidable in self.collisions:
                    self.collisions.remove(collidable)

                continue

            if collidable in self.collision_ignore:
                continue

            if self.velocity.x > 0:
                self.rect.right = collidable.rect.left
                self.collide_points['right'] = True

                callback_collision.append('right')

                if collidable not in self.collisions:
                    self.collisions.append(collidable)
       
                self.velocity.x = 0

            if self.velocity.x < 0:
                self.rect.left = collidable.rect.right
                self.collide_points['left'] = True

                if collidable not in self.collisions:
                    self.collisions.append(collidable)

                callback_collision.append('left')
                self.velocity.x = 0

        return callback_collision

    def apply_collision_y_default(self, collidables):
        callback_collision = list()

        for collidable in collidables:
            if not self.rect.colliderect(collidable.rect):
                if collidable in self.collision_ignore:
                    self.collision_ignore.remove(collidable)

                if collidable in self.collisions:
                    self.collisions.remove(collidable)
                    
                continue

            if collidable in self.collision_ignore:
                continue

            if self.velocity.y > 0:
                self.rect.bottom = collidable.rect.top
                self.collide_points['bottom'] = True

                callback_collision.append('bottom')

                if collidable not in self.collisions:
                    self.collisions.append(collidable)

                self.velocity.y = 0

            if self.velocity.y < 0:
                self.rect.top = collidable.rect.bottom
                self.collide_points['top'] = True

                callback_collision.append('top')

                if collidable not in self.collisions:
                    self.collisions.append(collidable)
            
                self.velocity.y = 0

        return callback_collision  

    def apply_gravity(self, dt):
        if not self.collide_points['bottom']:
            self.velocity.y += GRAVITY * dt if self.velocity.y < MAX_GRAVITY * dt else 0

        else:
            self.velocity.y = GRAVITY / dt

class Component(pygame.sprite.Sprite):
    ...

def check_pixel_collision(primary_sprite, secondary_sprite):
    collision = None
    if not isinstance(secondary_sprite, pygame.sprite.Group):
        group = pygame.sprite.Group(secondary_sprite)
        collision = pygame.sprite.spritecollide(primary_sprite, group, False, pygame.sprite.collide_mask)
        group.remove(secondary_sprite)

    else:
        collision = pygame.sprite.spritecollide(primary_sprite, secondary_sprite, False, pygame.sprite.collide_mask)

    return collision

def check_line_collision(start, end, sprites):
    clipped_sprites = list()

    for sprite in sprites:
        if sprite.rect.clipline(start, end):
            clipped_sprites.append(sprite)

    return clipped_sprites

def get_distance(primary_sprite, secondary_sprite):
    rx = abs(secondary_sprite.rect.x - primary_sprite.rect.x)
    ry = abs(secondary_sprite.rect.y - primary_sprite.rect.y)

    return math.sqrt(((rx **2) + (ry **2)))

def get_closest_sprite(primary_sprite, sprites):
    if len(sprites) == 1:
        return sprites[0]
            
    sprite_area = dict()

    for sprite in sprites:
        distance = get_distance(primary_sprite, sprite)
        sprite_area[sprite] = distance

    min_value = min(sprite_area.values())
    for sprite, area in sprite_area.items():
        if area == min_value:
            return sprite

    return None

def create_outline(sprite, color, display, size=1):
    surface = sprite.mask.to_surface(
        setcolor=color, 
        unsetcolor=pygame.Color(0, 0, 0, 0)
    )
    surface.set_colorkey(pygame.Color(0, 0, 0))

    for i in range(size):
        display.blit(surface, pygame.Vector2(sprite.rect.x - i, sprite.rect.y))
        display.blit(surface, pygame.Vector2(sprite.rect.x + i, sprite.rect.y))

        display.blit(surface, pygame.Vector2(sprite.rect.x, sprite.rect.y - i))
        display.blit(surface, pygame.Vector2(sprite.rect.x, sprite.rect.y + i))

        display.blit(surface, pygame.Vector2(sprite.rect.x - i, sprite.rect.y - i))
        display.blit(surface, pygame.Vector2(sprite.rect.x + i, sprite.rect.y + i))

        display.blit(surface, pygame.Vector2(sprite.rect.x - i, sprite.rect.y + i))
        display.blit(surface, pygame.Vector2(sprite.rect.x + i, sprite.rect.y - i))  