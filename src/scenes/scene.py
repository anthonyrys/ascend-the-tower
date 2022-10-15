from src.entities.entity import Tags

from src.ui.mouse import Mouse

import pygame
import math

class Scene():
    def __init__(self, surfaces, mouse, sprites=...):
        self.surfaces = surfaces
        self.background_surface, self.entity_surface, self.ui_surface = self.surfaces
        self.mouse = mouse

        self.sprites = sprites if isinstance(sprites, list) else list()
        self.frames = 0
    
    @staticmethod
    def sort_sprites(sprites):
        display_order = dict()
        unlabled = list()

        for sprite in sprites:
            if not isinstance(sprite.strata, int):
                unlabled.append(sprite)
                continue

            if sprite.strata in display_order:
                display_order[sprite.strata].append(sprite)

            else:
                display_order[sprite.strata] = list([sprite])

        if unlabled:
            display_order[-1] = list()

            for sprite in unlabled:
                display_order[-1].append(sprite)

        return display_order

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
    def get_distance(primary_sprite, secondary_sprite):
        rx = abs(secondary_sprite.rect.x - primary_sprite.rect.x)
        ry = abs(secondary_sprite.rect.y - primary_sprite.rect.y)

        return math.sqrt(((rx **2) + (ry **2)))

    @staticmethod
    def get_closest_sprite(primary_sprite, sprite_list):
        if len(sprite_list) == 1:
            return sprite_list[0]
            
        sprite_area = dict()

        for sprite in sprite_list:
            distance = Scene.get_distance(primary_sprite, sprite)
            sprite_area[sprite] = distance

        min_value = min(sprite_area.values())
        for sprite, area in sprite_area.items():
            if area == min_value:
                return sprite

        return None
        
    # <overridden by child classes>
    def display(self, screen):
        ...

    def add_sprites(self, sprites, *args):
        if not isinstance(sprites, list):
            sprites = list([sprites])

        for arg in args: 
            sprites.append(arg)

        for sprite in sprites:
            if not isinstance(sprite, pygame.sprite.Sprite):
                continue
                
            if sprite in self.sprites:
                continue

            self.sprites.append(sprite)

    def del_sprites(self, sprites, *args):
        if not isinstance(sprites, list):
            sprites = list([sprites])

        for arg in args: 
            sprites.append(arg)

        for sprite in sprites:
            if not sprite in self.sprites:
                continue

            self.sprites.remove(sprite)

    def check_mouse(self):
        sprites = list()
        entity_mouse = Mouse()
        entity_mouse.rect.center = self.mouse.rect.center + self.camera.offset

        interactables = [s for s in self.sprites if s.get_tag(Tags.INTERACTABLE)]

        for interactable in interactables:
            if not self.check_pixel_collision(entity_mouse, interactable):
                continue

            sprites.append(interactable)

        return sprites

    def mouse_down(self):
        for sprite in self.sprites:
            if not hasattr(sprite, 'on_mouse_down') or not callable(sprite.on_mouse_down):
                continue

            sprite.on_mouse_down(self)

    def mouse_up(self):
        for sprite in self.sprites:
            if not hasattr(sprite, 'on_mouse_up') or not callable(sprite.on_mouse_up):
                continue

            sprite.on_mouse_up(self)
