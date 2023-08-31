import pygame
import random
import math

def check_pixel_collision(primary_sprite, secondary_sprite):
    collision = None
    if not isinstance(secondary_sprite, pygame.sprite.Group):
        group = pygame.sprite.Group(secondary_sprite)
        collision = pygame.sprite.spritecollide(primary_sprite, group, False, pygame.sprite.collide_mask)
        group.remove(secondary_sprite)

    else:
        collision = pygame.sprite.spritecollide(primary_sprite, secondary_sprite, False, pygame.sprite.collide_mask)

    return collision

def check_line_collision(start, end, sprites, width=1):
    clipped_sprites = []

    if not isinstance(sprites, list):
        sprites = [sprites]

    for sprite in sprites:
        con = False
        for spr in clipped_sprites:
            if spr[0] == sprite:
                con = True

        if con:
            continue

        for i in range(width):
            if sprite.rect.clipline([start[0], start[1] + i], [end[0], end[1] + i]):
                clipped_sprites.append([sprite, sprite.rect.clipline([start[0], start[1] + i], [end[0], end[1] + i])])
                continue

            if sprite.rect.clipline([start[0], start[1] - i], [end[0], end[1] - i]):
                clipped_sprites.append([sprite, sprite.rect.clipline([start[0], start[1] - i], [end[0], end[1] - i])])
                continue

    return clipped_sprites

def get_distance(primary_sprite, secondary_sprite):
    if isinstance(primary_sprite, pygame.sprite.Sprite) and isinstance(secondary_sprite, pygame.sprite.Sprite):
        rx = abs(secondary_sprite.rect.x - primary_sprite.rect.x)
        ry = abs(secondary_sprite.rect.y - primary_sprite.rect.y)

        return math.sqrt(((rx **2) + (ry **2)))
        
    else:
        rx = abs(secondary_sprite[0] - primary_sprite[0])
        ry = abs(secondary_sprite[1] - primary_sprite[1])

        return math.sqrt(((rx **2) + (ry **2)))  

def get_closest_sprite(primary_sprite, sprites):
    if len(sprites) == 1:
        return sprites[0]
                
    sprite_area = {}

    for sprite in sprites:
        distance = get_distance(primary_sprite, sprite)
        sprite_area[sprite] = distance

    min_value = min(sprite_area.values())
    for sprite, area in sprite_area.items():
        if area == min_value:
            return sprite

    return None

def get_sprite_colors(primary_sprite, multiplier=1):
    if isinstance(primary_sprite, pygame.sprite.Sprite):
        image = primary_sprite.image
    else:
        image = primary_sprite

    iteration_threshold = .1
    iterations = int((((image.get_width() + image.get_height()) / 2) * iteration_threshold) * multiplier)

    colors = []
    for _ in range(iterations):
        found_pixel = False
        x = 0
        y = 0

        while not found_pixel:
            x = random.randint(0, image.get_width() - 1)
            y = random.randint(0, image.get_height() - 1)

            found_pixel = image.get_at((x, y)) != ((0, 0, 0, 0))
                
        colors.append(image.get_at([x, y]))

    return colors

def create_outline_edge(sprite, color, display, size=1):
    surface = pygame.Surface(sprite.image.get_size())
    surface.set_colorkey((0, 0, 0))
    for point in sprite.mask.outline():
        surface.set_at(point, color)

    for i in range(size):
        display.blit(surface, (sprite.rect.x + sprite.rect_offset[0] - i, sprite.rect.y + sprite.rect_offset[1]))
        display.blit(surface, (sprite.rect.x + sprite.rect_offset[0] + i, sprite.rect.y + sprite.rect_offset[1]))

        display.blit(surface, (sprite.rect.x + sprite.rect_offset[0], sprite.rect.y + sprite.rect_offset[1] - i))
        display.blit(surface, (sprite.rect.x + sprite.rect_offset[0], sprite.rect.y + sprite.rect_offset[1] + i))

        display.blit(surface, (sprite.rect.x + sprite.rect_offset[0] - i, sprite.rect.y + sprite.rect_offset[1] - i))
        display.blit(surface, (sprite.rect.x + sprite.rect_offset[0] + i, sprite.rect.y + sprite.rect_offset[1] + i))

        display.blit(surface, (sprite.rect.x + sprite.rect_offset[0] - i, sprite.rect.y + sprite.rect_offset[1] + i))
        display.blit(surface, (sprite.rect.x + sprite.rect_offset[0] + i, sprite.rect.y + sprite.rect_offset[1] - i))  

def create_outline_full(sprite, color, display, size=1):
    surface = sprite.mask.to_surface(
        setcolor=color, 
        unsetcolor=(0, 0, 0, 0)
    )
    surface.set_colorkey((0, 0, 0))

    for i in range(size):
        display.blit(surface, (sprite.rect.x - sprite.rect_offset[0] - i, sprite.rect.y - sprite.rect_offset[1]))
        display.blit(surface, (sprite.rect.x - sprite.rect_offset[0] + i, sprite.rect.y - sprite.rect_offset[1]))

        display.blit(surface, (sprite.rect.x - sprite.rect_offset[0], sprite.rect.y - sprite.rect_offset[1] - i))
        display.blit(surface, (sprite.rect.x - sprite.rect_offset[0], sprite.rect.y - sprite.rect_offset[1] + i))

        display.blit(surface, (sprite.rect.x - sprite.rect_offset[0] - i, sprite.rect.y - sprite.rect_offset[1] - i))
        display.blit(surface, (sprite.rect.x - sprite.rect_offset[0] + i, sprite.rect.y - sprite.rect_offset[1] + i))

        display.blit(surface, (sprite.rect.x - sprite.rect_offset[0] - i, sprite.rect.y - sprite.rect_offset[1] + i))
        display.blit(surface, (sprite.rect.x - sprite.rect_offset[0] + i, sprite.rect.y - sprite.rect_offset[1] - i))  