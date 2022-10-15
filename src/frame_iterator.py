from src.spritesheet_loader import Spritesheet

import pygame
import os

class PlayerFrames():
    def __init__(self):
        self.names = ['idle', 'run', 'jump', 'fall']

        self.imgs = dict()
        self.frames = dict()

        for name in self.names:
            self.imgs[name] = Spritesheet.load_frames(
            os.path.join('imgs', 'player', f'player-{name}.png'),
            os.path.join('data', 'player', f'player-{name}.json')
            )

            self.frames[name] = 0

        self.dt_frame_counter = 0

        self.scale = 2
        self.state = 'idle'

    def iterate(self, dt, et):
        img = None
        if len(self.imgs[self.state]) <= self.frames[self.state]:
            self.frames[self.state] = 0
            self.dt_frame_counter = 0

        img = self.imgs[self.state][self.frames[self.state]]

        self.dt_frame_counter += (1 * et) * dt
        self.frames[self.state] = round(self.dt_frame_counter)

        return pygame.transform.scale(img, pygame.Vector2(img.get_width() * self.scale, img.get_height() * self.scale))
