from src.constants import COLOR_VALUES_SECONDARY

from src.engine import (
    check_line_collision,
    get_distance,
    get_closest_sprite
)

from src.spritesheet_loader import load_standard

from src.entities.interactable import Interactable

import pygame
import os

class Mouse(pygame.sprite.Sprite):
    def __init__(self):
        self.images = load_standard(os.path.join('imgs', 'mouse.png'), os.path.join('data', 'imgs.json'), 'mouse')
        for i in range(len(self.images)):
            self.images[i-1] = pygame.transform.scale(self.images[i-1], pygame.Vector2(32, 32))

        self.image = self.images[0]
        self.image = self.mask.to_surface(
            setcolor=pygame.Color(255, 255, 255), 
            unsetcolor=pygame.Color(0, 0, 0, 0)
        )

        self.rect = self.image.get_rect()

    @property
    def mask(self):
        return pygame.mask.from_surface(self.image)

    def set_selected_interactable(self, scene):
        interactable_sprites = check_line_collision(
            scene.player.rect.center,
            self.rect.center + scene.camera.offset,
            [s for s in scene.sprites if isinstance(s, Interactable)]
        )
        
        for sprite in interactable_sprites:
            if sprite.interacting or get_distance(scene.player, sprite) > sprite.interact_dist:
                interactable_sprites.remove(sprite)

        if not interactable_sprites:
            return

        get_closest_sprite(scene.player, interactable_sprites).on_select(scene.player)

    def set_image(self, player):
        ...

    def display(self, scene, player=...):
        if player == ...:  
            self.rect.center = pygame.mouse.get_pos()
            scene.ui_surface.blit(self.image, self.rect)
            
            return

        self.set_image(player)
        self.image = self.mask.to_surface(
            setcolor=COLOR_VALUES_SECONDARY[player.color], 
            unsetcolor=pygame.Color(0, 0, 0, 0)
        )

        self.rect.center = pygame.mouse.get_pos()
        self.set_selected_interactable(scene)

        scene.ui_surface.blit(self.image, self.rect)
