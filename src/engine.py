from src.constants import SCREEN_DIMENSIONS

import pygame
import random
import math
        
class BoxCamera():
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
            intensity = round((self.camera_shake_intensity) * (1 - math.cos((abs_prog * math.pi) / 2)))

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
                (offset.x - self.start_pos.x) * (1 - math.pow(1 - abs_prog, 5)),
                (offset.y - self.start_pos.y) * (1 - math.pow(1 - abs_prog, 5)),
            )

            self.camera_tween_frames += 1 * dt

            self.offset = tweened_offset
            return tweened_offset

        else:
            self.offset = offset
            return offset

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

def apply_collision_x_def(sprite, collidables):
    callback_collision = list()

    for collidable in collidables:
        if not sprite.rect.colliderect(collidable.rect):
            if collidable in sprite.collision_ignore:
                sprite.collision_ignore.remove(collidable)
                
            continue

        if collidable in sprite.collision_ignore:
            continue

        if sprite.velocity.x > 0:
            sprite.rect.right = collidable.rect.left
            sprite.collide_points['right'] = True

            callback_collision.append('right')
            sprite.velocity.x = 0

        if sprite.velocity.x < 0:
            sprite.rect.left = collidable.rect.right
            sprite.collide_points['left'] = True

            callback_collision.append('left')
            sprite.velocity.x = 0

    return callback_collision

def apply_collision_y_def(sprite, collidables):
    callback_collision = list()

    for collidable in collidables:
        if not sprite.rect.colliderect(collidable.rect):
            if collidable in sprite.collision_ignore:
                sprite.collision_ignore.remove(collidable)
                
            continue

        if collidable in sprite.collision_ignore:
            continue

        if sprite.velocity.y > 0:
            sprite.rect.bottom = collidable.rect.top
            sprite.collide_points['bottom'] = True

            callback_collision.append('bottom')
            sprite.velocity.y = 0

        if sprite.velocity.y < 0:
            sprite.rect.top = collidable.rect.bottom
            sprite.collide_points['top'] = True

            callback_collision.append('top')
            sprite.velocity.y = 0

    return callback_collision    

def apply_point_rotation(sprite, position, point, angle):
    rect = sprite.image.get_rect(topleft = (position.x - point.x, position.y - point.y))
    offset = (position - rect.center).rotate(-angle)
    center = (position.x - offset.x, position.y - offset.y)

    sprite.image = pygame.transform.rotate(sprite.original_image, angle).convert_alpha()
    sprite.rect = sprite.image.get_rect(center = center)
