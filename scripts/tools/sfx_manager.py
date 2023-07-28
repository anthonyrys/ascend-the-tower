import pygame
import os

class Sfx:
    SOUNDS = {}
    SETTINGS = {}

    def init():
        for file in os.listdir(os.path.join('resources', 'sound_fx')):
            Sfx.SOUNDS[file.split('.')[0]] = pygame.mixer.Sound(os.path.join('resources', 'sound_fx', file))

    def play(sound):
        if sound not in Sfx.SOUNDS:
            print(f'[SFX_MANAGER] Sound "{sound}" not found.')
            return
    
        Sfx.SOUNDS[sound].play()
