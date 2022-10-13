import pygame
import json

class Spritesheet():
    @staticmethod
    def load_frames(pngpath, jsonpath):
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

        return imgs
