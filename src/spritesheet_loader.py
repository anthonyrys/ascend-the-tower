import pygame
import json
import os

def load_standard(pngpath, name):
    jsonpath = os.path.join('data', 'imgs.json')
    sheet, data = None, None
    imgs = list()
            
    sheet = pygame.image.load(pngpath).convert_alpha()
    data_json = json.load(open(jsonpath))
    data = data_json[name]

    width = data['spritesize']['width']
    height = data['spritesize']['height']

    for i in range(int(data['sheetsize']['width'] / width)):
        x = width * i

        img = pygame.Surface((width, height)).convert_alpha()
        img.set_colorkey((0, 0, 0))
        img.blit(sheet, (0, 0), (x, 0, width, height))

        imgs.append(img)

    return imgs

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
        img.set_colorkey((0, 0, 0))
        img.blit(sheet, (0, 0), (x, 0, width, height))

        for _ in range(duration):
            imgs.append(img)

    return imgs
