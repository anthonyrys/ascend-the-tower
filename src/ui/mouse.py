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
        self.images = load_standard(os.path.join('imgs', 'mouse.png'), 'mouse')
        for i in range(len(self.images)):
            self.images[i-1] = pygame.transform.scale(self.images[i-1], (32, 32))

        self.image = self.images[0]
        self.image = self.mask.to_surface(
            setcolor=(255, 255, 255), 
            unsetcolor=(0, 0, 0, 0)
        )

        self.rect = self.image.get_rect()

    @property
    def mask(self):
        return pygame.mask.from_surface(self.image)

    def set_selected_interactable(self, scene, player):
        if player.states['interacting']:
            return

        if scene.paused:
            return

        interactable_sprites = check_line_collision(
            scene.player.rect.center,
            (self.rect.center[0] + scene.camera_offset[0], self.rect.center[1] + scene.camera_offset[1]),
            [s for s in scene.sprites if isinstance(s, Interactable)]
        )
        
        if not interactable_sprites:
            return
            
        interactable_sprite = get_closest_sprite(scene.player, interactable_sprites)
        
        if get_distance(scene.player, interactable_sprite) <= interactable_sprite.interact_dist:
            interactable_sprite.on_select()

    def set_image(self, player):
        if player.states['interacting'] and not player.interact_obj.independent:
            if self.image is not self.images[1]:
                self.image = self.images[1]
            
        else:
            if self.image is not self.images[0]:
                self.image = self.images[0]

        self.image = self.mask.to_surface(
            setcolor=COLOR_VALUES_SECONDARY[player.color], 
            unsetcolor=(0, 0, 0, 0)
        )

    def display(self, scene, player=None):
        if not player:  
            self.rect.center = pygame.mouse.get_pos()
            scene.ui_surface.blit(self.image, self.rect)
            
            return

        self.set_image(player)

        self.rect.center = pygame.mouse.get_pos()
        self.set_selected_interactable(scene, player)

        scene.ui_surface.blit(self.image, self.rect)
