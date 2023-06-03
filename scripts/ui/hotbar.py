'''
Holds the Hotbar and AbilityFrame class.
'''

from scripts.engine import Frame, Inputs

from scripts.ui.card import Card
from scripts.ui.text_box import TextBox

import pygame
import os

class AbilityFrame(Frame):
    '''
    Frame that displays ability information

    Variables:
        player: the initialized player class.
        key: the player's input key for the ability.

        pulse_info: information on how the image should be pulsed.

        cooldown_alpha: alpha value for when the ability is on cooldown.

        background: background surface for the ability frame.
        cooldown: cooldown surface for the ability frame.
        original_cooldown: an original copy of the cooldown surface.
        frame: the decorative frame for the ability.

    Methods:
        set_pulse(): sets the values of pulse_info.
    '''

    def __init__(self, player, key):
        IMG_SCALE = 2.5
    
        img = pygame.image.load(os.path.join('imgs', 'ui', 'hotbar', 'ability-frame.png')).convert_alpha()
        img = pygame.transform.scale(img, (img.get_width() * IMG_SCALE, img.get_height() * IMG_SCALE))

        super().__init__((0, 0), pygame.Surface(img.get_size()).convert_alpha(), None, 3, None)
        self.image.set_colorkey((0, 0, 0))
        
        self.player = player
        self.key = key

        self.pulse_info = {
            'surface': None,
            'frames': 0,
            'frames_max': 0 
        }

        self.cooldown_alpha = 125

        self.background = pygame.Surface(self.image.get_size()).convert_alpha()
        self.background.fill((203, 203, 203))

        self.cooldown = pygame.Surface(self.image.get_size()).convert_alpha()
        self.cooldown.fill((0, 0, 0, 125))

        self.original_cooldown = self.cooldown.copy()

        self.frame = img

    def set_pulse(self, frames, color):
        self.pulse_info['surface'] = self.image.copy()
        self.pulse_info['surface'] = pygame.mask.from_surface(self.pulse_info['surface']).to_surface(setcolor=color, unsetcolor=(0, 0, 0))

        self.pulse_info['frames'] = frames
        self.pulse_info['frames_max'] = frames

    def display(self, position, surface, dt):
        self.image.fill((0, 0, 0))
        self.rect.x, self.rect.y = position

        ability = self.player.abilities[self.key]
        info = ability.fetch()

        text = TextBox((0, 0), pygame.key.name(Inputs.KEYBINDS[self.key][0]), size=.7).image
        text_pos = [
            position[0] + self.image.get_width() * .5,
            self.image.get_rect().bottom + text.get_height() * .75
        ]

        if info['icon'] not in Card.ICONS['ability']:
            info['icon'] = 'default'

        icon = Card.ICONS['ability'][info['icon']].copy()
        icon = pygame.transform.scale(icon, (icon.get_width() * .55, icon.get_height() * .55))

        cooldown_percentage = ability.ability_info['cooldown'] / ability.ability_info['cooldown_timer']
        self.cooldown = pygame.transform.scale(self.original_cooldown, (self.original_cooldown.get_width(), self.original_cooldown.get_height() * cooldown_percentage))

        self.image.blit(self.background, (0, 0))
        self.image.blit(icon, icon.get_rect(center=self.image.get_rect().center))
        self.image.blit(self.cooldown, self.cooldown.get_rect(bottom=self.image.get_rect().bottom))
        self.image.blit(self.frame, (0, 0))

        if cooldown_percentage > 0 and self.image.get_alpha() != self.cooldown_alpha:
            self.image.set_alpha(self.cooldown_alpha)
            text.set_alpha(self.cooldown_alpha)

        elif cooldown_percentage <= 0 and self.image.get_alpha() != 255:
            self.image.set_alpha(255)
            text.set_alpha(255)

            self.set_pulse(20, (255, 255, 255))

        if self.pulse_info['frames'] > 0:
            self.pulse_info['surface'].set_alpha((self.pulse_info['frames'] / self.pulse_info['frames_max']) * 255)
            
            self.image.blit(self.pulse_info['surface'], (0, 0))
            self.pulse_info['frames'] -= 1 * dt

        surface.blit(self.image, position)
        surface.blit(text, text.get_rect(center=text_pos))
    
class Hotbar(Frame):
    '''
    Manages and sets the positions for AbilityFrames.

    Variables:
        player: the initialized player class.

        frames: a list of AbilityFrames.
        frame_padding: padding between each frame.
    '''

    def __init__(self, player, position, strata):
        super().__init__(position, pygame.Surface((300, 125)).convert_alpha(), None, strata, None)
        self.sprite_id = 'hotbar'
        self.rect.center = position

        self.player = player

        self.frames = []
        self.frame_padding = 12

        for ability in player.abilities.items():
            if ability[0] in ['primary', 'dash']:
                continue

            self.frames.append(AbilityFrame(self.player, ability[0]))

    def display(self, scene, dt):
        self.image.fill((0, 0, 0, 1))
        frames = [f for f in self.frames if self.player.abilities[f.key] is not None]
        if not frames:
            return
        
        width = (len(frames) * frames[0].image.get_width()) + ((len(frames) - 1) * self.frame_padding)
        surface = pygame.Surface((width, self.image.get_height()))
        surface.set_colorkey((0, 0, 0))

        x = 0
        for frame in frames:
            frame.display((x, 0), surface, dt)
            x += frame.image.get_width() + self.frame_padding

        self.image.blit(surface, surface.get_rect(center=self.image.get_rect().center))
        super().display(scene, dt)
