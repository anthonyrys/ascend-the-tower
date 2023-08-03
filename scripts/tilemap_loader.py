from scripts.tools.spritesheet_loader import load_spritesheet

from scripts.entities.tiles import Block, Ramp, get_all_tiles
from scripts.entities.interactables import get_all_interactables
from scripts.entities.decoration import get_all_decoration

import pygame
import json
import os

TILEMAP_FOLDER_PATH = os.path.join('resources', 'data', 'tilemap_editor')

def load_tilemap(name):
    path = os.path.join(TILEMAP_FOLDER_PATH, name)
    
    with open(os.path.join(path, 'tilemap.json')) as t:
        data = json.load(t)
    
    dimensions = [
        data['config']['tile']['dimensions'][0] * data['config']['tilemap']['dimensions'][0],
        data['config']['tile']['dimensions'][1] * data['config']['tilemap']['dimensions'][1]
    ]

    surface = pygame.Surface(dimensions, pygame.SRCALPHA).convert_alpha()
    tiles = []
    flags = {}

    images = {}
    for image in data['config']['images']:
        images[image] = {}
        images[image]['imgs'] = load_spritesheet(os.path.join(path, data['config']['images'][image]['path']), scale=2)
        images[image]['tiles'] = data['config']['images'][image]['tiles']
    
    tile_classes = {}
    for tile_class in get_all_tiles():
        tile_classes[tile_class[0].lower()] = tile_class[1]
    
    interactable_classes = {}
    for interactable_class in get_all_interactables():
        interactable_classes[interactable_class[0].lower()] = interactable_class[1]

    decoration_classes = {}
    for decoration_class in get_all_decoration():
        decoration_classes[decoration_class[0].lower()] = decoration_class[1]

    for tile_data in data['tiles']:
        if tile_data['tileset'] == 'flags':
            if tile_data['tile'] not in flags:
                flags[tile_data['tile']] = []

            flags[tile_data['tile']].append(tile_data['position'])

        elif tile_data['tile'].split('_')[0] == 'ramp':
            img = images[tile_data['tileset']]['imgs'][tile_data['index']].copy()
            img = pygame.transform.rotate(img, -tile_data['orientation'])
            img = pygame.transform.flip(img, tile_data['flipped'], False)

            direction = tile_data['tile'].split('_')[1]
            upside_down = False

            if direction == 'left':
                if tile_data['orientation'] in [90, 180] or tile_data['flipped']:
                    direction = 'right'

                if tile_data['orientation'] in [180, 270]:
                    upside_down = True

            elif direction == 'right':
                if tile_data['orientation'] in [180, 270] or tile_data['flipped']:
                    direction = 'left'

                if tile_data['orientation'] in [90, 180]:
                    upside_down = True

            if upside_down:
                tile = Block(
                    tile_data['position'],
                    img,
                    None,
                    tile_data['strata']
                )

            else:
                tile = Ramp(
                    tile_data['position'],
                    img,
                    direction,
                    tile_data['strata']
                )

            tiles.append(tile)

        else:
            if tile_data['tile'] in tile_classes.keys():
                img = images[tile_data['tileset']]['imgs'][tile_data['index']].copy()
                img = pygame.transform.rotate(img, -tile_data['orientation'])
                img = pygame.transform.flip(img, tile_data['flipped'], False)

                tile = tile_classes[tile_data['tile']](
                    tile_data['position'],
                    img,
                    None,
                    tile_data['strata']
                )

                tiles.append(tile)

            elif tile_data['tile'] in interactable_classes.keys():
                img = images[tile_data['tileset']]['imgs'][tile_data['index']].copy()
                img = pygame.transform.rotate(img, -tile_data['orientation'])
                img = pygame.transform.flip(img, tile_data['flipped'], False)

                interactable = interactable_classes[tile_data['tile']](
                    tile_data['position'],
                    img,
                    None,
                    tile_data['strata']
                )

                tiles.append(interactable)

            elif tile_data['tile'] in decoration_classes.keys():
                img = images[tile_data['tileset']]['imgs'][tile_data['index']].copy()
                img = pygame.transform.rotate(img, -tile_data['orientation'])
                img = pygame.transform.flip(img, tile_data['flipped'], False)

                decoration = decoration_classes[tile_data['tile']](
                    tile_data['position'],
                    img,
                    None,
                    tile_data['strata']
                )

                tiles.append(decoration)

            else:
                print(f'[LOAD_TILEMAP] Cannot resolve tile type: {tile_data["tile"]}')

    return {
        'surface': surface,
        'tiles': tiles,
        'flags': flags
    }
