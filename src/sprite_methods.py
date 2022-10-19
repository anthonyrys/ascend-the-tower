import pygame
import math

class Methods():
    @staticmethod
    def check_pixel_collision(primary_sprite, secondary_sprite):
        collision = None
        if not isinstance(secondary_sprite, pygame.sprite.Group):
            group = pygame.sprite.Group(secondary_sprite)
            collision = pygame.sprite.spritecollide(primary_sprite, group, False, pygame.sprite.collide_mask)
            group.remove(secondary_sprite)

        else:
            collision = pygame.sprite.spritecollide(primary_sprite, secondary_sprite, False, pygame.sprite.collide_mask)

        return collision

    @staticmethod
    def check_line_collision(start, end, sprites):
        clipped_sprites = list()

        for sprite in sprites:
            if sprite.rect.clipline(start, end):
                clipped_sprites.append(sprite)

        return clipped_sprites

    @staticmethod
    def get_distance(primary_sprite, secondary_sprite):
        rx = abs(secondary_sprite.rect.x - primary_sprite.rect.x)
        ry = abs(secondary_sprite.rect.y - primary_sprite.rect.y)

        return math.sqrt(((rx **2) + (ry **2)))

    @staticmethod
    def get_closest_sprite(primary_sprite, sprites):
        if len(sprites) == 1:
            return sprites[0]
            
        sprite_area = dict()

        for sprite in sprites:
            distance = Methods.get_distance(primary_sprite, sprite)
            sprite_area[sprite] = distance

        min_value = min(sprite_area.values())
        for sprite, area in sprite_area.items():
            if area == min_value:
                return sprite

        return None

    @staticmethod
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
