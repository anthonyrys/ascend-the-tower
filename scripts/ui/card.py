from scripts.engine import Frame

from scripts.services.spritesheet_loader import load_spritesheet

import pygame
import random
import os

class Card(Frame):
    IMG_SCALE = 4

    BASES = []
    ICONS = {
        'talent': {},
        'ability': {}
    }
    SYMBOLS = {
        'type': {
            'talent': None,
            'ability': None,
        },

        'action': {
            'damage': None, 
            'heal': None, 
            'resistance/immunity': None,
            'speed': None, 
            'cooldown': None, 
            'other': None
        },
        
        'talent': {
            'ability': None, 
            'attack/kill': None, 
            'hurt/death': None, 
            'passive': None, 
            'other': None
        },

        'ability': {
            'contact': None,
            'physical': None,
            'magical': None,
            'status': None, 
            'special': None
        }
    }

    TYPE_KEYS = ['talent', 'ability']
    ACTION_KEYS = ['damage', 'heal', 'resistance/immunity', 'speed', 'cooldown', 'other']
    TALENT_KEYS = ['ability', 'attack/kill', 'hurt/death', 'passive', 'other']
    ABILITY_KEYS = ['contact', 'physical', 'magical', 'status', 'special']
    
    @staticmethod
    def init():
        for base in load_spritesheet(os.path.join('imgs', 'ui', 'card', 'card-base.png')):
            img = pygame.transform.scale(base, (base.get_width() * Card.IMG_SCALE, base.get_height() * Card.IMG_SCALE)).convert_alpha()
            Card.BASES.append(img)
    
        for icon in os.listdir(os.path.join('imgs', 'ui', 'card', 'talents')):
            img = pygame.image.load(os.path.join('imgs', 'ui', 'card', 'talents', icon)).convert_alpha()                 
            img = pygame.transform.scale(img, (img.get_width() * Card.IMG_SCALE, img.get_height() * Card.IMG_SCALE)).convert_alpha()

            Card.ICONS['talent'][icon.split('.')[0]] = img

        for icon in os.listdir(os.path.join('imgs', 'ui', 'card', 'abilities')):
            img = pygame.image.load(os.path.join('imgs', 'ui', 'card', 'abilities', icon)).convert_alpha()
            img = pygame.transform.scale(img, (img.get_width() * Card.IMG_SCALE, img.get_height() * Card.IMG_SCALE)).convert_alpha()

            Card.ICONS['ability'][icon.split('.')[0]] = img


        for index, img in enumerate(load_spritesheet(os.path.join('imgs', 'ui', 'card', 'symbols', 'card-type.png'))):
            img = pygame.transform.scale(img, (img.get_width() * Card.IMG_SCALE, img.get_height() * Card.IMG_SCALE)).convert_alpha()
            Card.SYMBOLS['type'][Card.TYPE_KEYS[index]] = img

        for index, img in enumerate(load_spritesheet(os.path.join('imgs', 'ui', 'card', 'symbols', 'card-action.png'))):
            img = pygame.transform.scale(img, (img.get_width() * Card.IMG_SCALE, img.get_height() * Card.IMG_SCALE)).convert_alpha()
            Card.SYMBOLS['action'][Card.ACTION_KEYS[index]] = img

        for index, img in enumerate(load_spritesheet(os.path.join('imgs', 'ui', 'card', 'symbols', 'card-talents.png'))):
            img = pygame.transform.scale(img, (img.get_width() * Card.IMG_SCALE, img.get_height() * Card.IMG_SCALE)).convert_alpha()
            Card.SYMBOLS['talent'][Card.TALENT_KEYS[index]] = img

        for index, img in enumerate(load_spritesheet(os.path.join('imgs', 'ui', 'card', 'symbols', 'card-abilities.png'))):
            img = pygame.transform.scale(img, (img.get_width() * Card.IMG_SCALE, img.get_height() * Card.IMG_SCALE)).convert_alpha()
            Card.SYMBOLS['ability'][Card.ABILITY_KEYS[index]] = img

    def draw(self):
        img = Card.BASES[random.randint(0, len(Card.BASES) - 1)].copy()
        icon = None
        symbols = None

        if self.info['icon'] not in Card.ICONS[self.info['type']]:
            self.info['icon'] = 'default'

        icon = Card.ICONS[self.info['type']][self.info['icon']].copy()

        width = 0
        height = None
        padding = 1 * Card.IMG_SCALE

        for symbol in self.info['symbols']:
            width += symbol.get_width()
            height = symbol.get_height()

        symbols = pygame.Surface((width + (padding * (len(self.info['symbols']) - 1)), height)).convert_alpha()
        symbols.fill((0, 0, 0, 0))

        x = 0
        for symbol in self.info['symbols']:
            sym = symbol.copy()
            symbols.blit(sym, (x, 0))
            x += symbol.get_width() + padding

        img.blit(icon, (icon.get_rect(center = (img.get_width() * .5, img.get_height() * .4))))
        img.blit(symbols, (symbols.get_rect(center = (img.get_width() * .5, img.get_height() * .75))))

        return img

    def __init__(self, position, info):
        self.info = info
        super().__init__(position, self.draw(), None, 3)