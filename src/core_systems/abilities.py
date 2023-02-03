from src.engine import Inputs

import pygame

class Ability:
    ABILITY_FLAGS = []

    def __init__(self, character):
        self.character = character
        self.passive = True

        self.ability_id = None
        self.ability_flags = []

        self.ability_info = {
            'cooldown_timer': 0,
            'cooldown': 0
        }

        self.keybind_info = {
            'double_tap': False,
            'keybinds': []
        }

    def call(self, scene, keybind=None):
        ...
    
    def update(self, scene, dt):
        if self.ability_info['cooldown'] > 0:
            self.ability_info['cooldown'] -= 1 * dt

class Dash(Ability):
    def __init__(self, character):
        super().__init__(character)

        self.passive = False

        self.ability_id = 'a000'

        self.ability_info['cooldown_timer'] = 35
        self.ability_info['velocity'] = character.movement_info['max_movespeed'] * 3

        self.keybind_info['double_tap'] = True
        self.keybind_info['keybinds'] = ['left', 'right']

    def call(self, scene, keybind=None):
        if self.ability_info['cooldown'] > 0:
            return
        
        self.ability_info['cooldown'] = self.ability_info['cooldown_timer']

        if keybind == 'left':
            self.character.velocity[0] = -self.ability_info['velocity']
        elif keybind == 'right':
            self.character.velocity[0] = self.ability_info['velocity']
