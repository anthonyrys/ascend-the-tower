import pygame
import os
import json

class PlayerFrames():
    @staticmethod
    def get_images(pngpath, jsonpath):
        sheet, data = None, None
        imgs = list()
            
        sheet = pygame.image.load(pngpath).convert_alpha()
        data = json.load(open(jsonpath))

        width = data['spritesize']['width']
        height = data['spritesize']['height']

        for i in data['frames'].keys():
            x = width * int(i)
            duration = data['frames'][f'{i}']['duration']

            img = pygame.Surface((width, height)).convert_alpha()
            img.set_colorkey(pygame.Color((0, 0, 0)))
            img.blit(sheet, pygame.Vector2(0, 0), (x, 0, width, height))

            for _ in range(duration):
                imgs.append(img)

        return imgs, data['priority']

    def __init__(self):
        self.names = ['idle', 'run', 'jump', 'fall']

        self.imgs, self.priority = dict(), dict()
        self.frames = dict()

        for name in self.names:
            self.imgs[name], self.priority[name] = self.get_images(
            os.path.join('imgs', 'player', f'player-{name}.png'),
            os.path.join('data', 'player', f'player-{name}.json')
            )

            self.frames[name] = 0

        self.scale = 2
        self.state = 'idle'

    def iterate_frame(self):
        img = None
        if len(self.imgs[self.state]) == self.frames[self.state]:
            self.frames[self.state] = 0

        img = self.imgs[self.state][self.frames[self.state]]
        self.frames[self.state] += 1

        return pygame.transform.scale(img, pygame.Vector2(img.get_width() * self.scale, img.get_height() * self.scale))