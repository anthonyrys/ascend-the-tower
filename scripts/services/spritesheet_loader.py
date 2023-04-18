'''
Holds the method that splites spritesheets into usable pygame surfaces.
'''

import pygame
import json
import os

config = json.load(open(os.path.join('data', 'config.json')))
spritesheet_stop_code = tuple(config['spritesheet_stop_code'])

def load_spritesheet(pngpath, frames=None, colorkey=(0, 0, 0)):
    imgs = []   
    sheet = pygame.image.load(pngpath).convert_alpha()

    width = sheet.get_width()
    height = sheet.get_height()

    img_count = 0
    start, stop = 0, 0
    i = 0

    for i in range(width):
        if sheet.get_at((i, 0)) != spritesheet_stop_code:
            continue
    
        stop = i
        img = pygame.Surface((stop - start, height)).convert_alpha()
        img.set_colorkey(colorkey)
        img.blit(sheet, (0, 0), (start, 0, stop - start, height))

        if frames:
            for _ in range(frames[img_count]):
                imgs.append(img)

        else:
            imgs.append(img)

        img_count += 1
        start = stop + 1

    return imgs
