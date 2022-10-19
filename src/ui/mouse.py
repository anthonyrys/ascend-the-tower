from src.entities.entity import Tags

from src.constants import COLOR_VALUES_SECONDARY
from src.spritesheet_loader import Spritesheet
from src.sprite_methods import Methods

import pygame
import os

class Mouse(pygame.sprite.Sprite):
    def __init__(self):
        self.images = Spritesheet.load_standard(os.path.join('imgs', 'mouse.png'), os.path.join('data', 'mouse.json'))
        for img in self.images:
            img = pygame.transform.scale(img, pygame.Vector2(20, 20))

        self.image = self.images[0]
        self.image = self.mask.to_surface(
            setcolor=pygame.Color(255, 255, 255), 
            unsetcolor=pygame.Color(0, 0, 0, 0)
        )

        self.rect = self.image.get_rect()

    @property
    def mask(self):
        return pygame.mask.from_surface(self.image)

    def set_hover(self, scene):
        interactable_sprites = Methods.check_line_collision(
            scene.player.rect.center,
            self.rect.center + scene.camera.offset,
            [s for s in scene.sprites if s.get_tag(Tags.INTERACTABLE)]
        )
        
        for sprite in interactable_sprites:
            if sprite.interacting or Methods.get_distance(scene.player, sprite) > sprite.interact_dist:
                interactable_sprites.remove(sprite)

        if not interactable_sprites:
            return

        Methods.get_closest_sprite(scene.player, interactable_sprites).on_select(scene.player)

    def set_image(self, player):
        if player.states['interacting']:
            if player.interact_obj.independent:
                return

            if self.image != self.images[1]:
                self.image = self.images[1]

        else:
            if self.image != self.images[0]:
                self.image = self.images[0]

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
        self.set_hover(scene)

        scene.ui_surface.blit(self.image, self.rect)
