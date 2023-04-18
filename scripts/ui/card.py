'''
Holds the card class.
'''

from scripts.constants import SCREEN_DIMENSIONS
from scripts.engine import Frame, Easings, create_outline_edge

from scripts.services.spritesheet_loader import load_spritesheet

from scripts.ui.text_box import TextBox

import pygame
import random
import os

class Card(Frame):
    '''
    Used to display ability and talent information.

    Variables:
        IMG_SCALE: scale factor the images.
        BASES: images of the card bases.
        
        ICONS: a collection of icons for the different types of talents/abilities.
        SYMBOLS: a collection of symbols to display the descriptions of the different talents/abilities.

        draw: the talent/ability class that was drawn.
        info: the information of the draw variable; using fetch().

        drawed_cards: a list of the other drawn cards.
        on_select: whether the card has been selected.

        tween_info: information on the easing and tweening of the object.
        hover_info: information on the position and easing of the object when it is hovering.

        hover_texts: a dictonary of TextBoxes to display when the card is hovering.

    Methods:
        create_card(): creates a new card to display.

        on_hover_start(): called when mouse is hovering over the card.
        on_hover_start(): called when mouse has stopped hovering over the card.
    '''
    
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

        for symbol in os.listdir(os.path.join('imgs', 'ui', 'card', 'symbols')):
            name = symbol.split('-')[1].split('.')[0]
            for index, img in enumerate(load_spritesheet(os.path.join('imgs', 'ui', 'card', 'symbols', symbol))):
                keys = list(Card.SYMBOLS[name].keys())
                img = pygame.transform.scale(img, (img.get_width() * Card.IMG_SCALE, img.get_height() * Card.IMG_SCALE)).convert_alpha()
                Card.SYMBOLS[name][keys[index]] = img

    def __init__(self, position, draw, spawn=None):
        self.draw = draw
        self.info = draw.fetch()

        super().__init__(position, self.create_card(), None, 3)

        self.sprite_id = 'card'

        self.drawed_cards = None
        self.on_select = None

        self.tween_info = {
            'frames': 0,
            'frames_max': 0,
            'easing': getattr(Easings, 'ease_out_cubic'),

            'position': [],
            'base_position': [],

            'flag': 'init',
            'on_finished': None
        }

        self.hover_info = {
            'x': self.rect.x,
            'y': self.rect.y - 10,

            'frames': 5,
            'easing': getattr(Easings, 'ease_out_cubic'),
        }

        self.hover_rect.width = self.rect.width
        self.hover_rect.height = self.rect.height + 16

        color = (255, 255, 255)

        self.hover_texts = {}

        self.hover_texts['name'] = TextBox((0, self.rect.bottom + 50), self.draw.DESCRIPTION['name'], color=color)
        self.hover_texts['name'].rect.x = (SCREEN_DIMENSIONS[0] * .5) - (self.hover_texts['name'].image.get_width() * .5)
    
        if draw.DRAW_SPECIAL:
            self.hover_texts['special'] = TextBox((0, self.rect.bottom + 100), draw.DRAW_SPECIAL[0], size=.5, color=draw.DRAW_SPECIAL[1])
            self.hover_texts['special'].rect.x = (SCREEN_DIMENSIONS[0] * .5) - (self.hover_texts['special'].image.get_width() * .5)

            self.hover_texts['description'] = TextBox((0, self.rect.bottom + 140), self.draw.DESCRIPTION['description'], size=.5, color=color)
            self.hover_texts['description'].rect.x = (SCREEN_DIMENSIONS[0] * .5) - (self.hover_texts['description'].image.get_width() * .5)

        else:
            self.hover_texts['description'] = TextBox((0, self.rect.bottom + 110), self.draw.DESCRIPTION['description'], size=.5, color=color)
            self.hover_texts['description'].rect.x = (SCREEN_DIMENSIONS[0] * .5) - (self.hover_texts['description'].image.get_width() * .5)

        if spawn is not None:
            if spawn == 'y':
                self.rect.y = 0 - (self.image.get_height())

            if spawn == 'x':
                self.rect.x = 0 - (self.image.get_width())

            self.tween_info['position'] = [self.original_rect.x, self.original_rect.y]
            self.tween_info['base_position'] = [self.rect.x, self.rect.y]

            self.tween_info['frames'] = 0
            self.tween_info['frames_max'] = 30

    def create_card(self):
        img = random.choice(Card.BASES).copy()

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

    def on_hover_start(self, scene):
        if self.tween_info['flag'] == 'init':
            return
        
        if self.tween_info['flag'] == 'del':
            return
        
        self.hovering = True
        self.tween_info['position'] = [self.hover_info['x'], self.hover_info['y']]
        self.tween_info['base_position'] = [self.original_rect.x, self.original_rect.y]

        self.tween_info['frames'] = 0
        self.tween_info['frames_max'] = self.hover_info['frames']

        self.tween_info['easing'] = self.hover_info['easing']
        self.tween_info['flag'] = 'hover_start'

        scene.add_sprites(list(self.hover_texts.values()))

    def on_hover_end(self, scene):
        if self.tween_info['flag'] == 'init':
            return
        
        if self.tween_info['flag'] == 'del':
            return

        self.hovering = False
        self.tween_info['position'] = [self.original_rect.x, self.original_rect.y]
        self.tween_info['base_position'] = [self.rect.x, self.rect.y]

        self.tween_info['frames'] = 0
        self.tween_info['frames_max'] = self.hover_info['frames']

        self.tween_info['easing'] = self.hover_info['easing']
        self.tween_info['flag'] = 'hover_end'

        scene.del_sprites(list(self.hover_texts.values()))

    def on_mouse_down(self, scene, event):
        if not self.hovering:
            return
        
        if event != 1:
            return

        if self.tween_info['flag'] == 'init' or self.tween_info['flag'] == 'del':
            return

        self.on_hover_end(scene)
        self.on_select(self, self.drawed_cards)

    def display(self, scene, dt):
        if self.tween_info['frames'] < self.tween_info['frames_max']:
            abs_prog = self.tween_info['frames'] / self.tween_info['frames_max']

            self.rect.x = self.tween_info['base_position'][0] + (self.tween_info['position'][0] - self.tween_info['base_position'][0]) * self.tween_info['easing'](abs_prog)
            self.rect.y = self.tween_info['base_position'][1] + (self.tween_info['position'][1] - self.tween_info['base_position'][1]) * self.tween_info['easing'](abs_prog)

            self.tween_info['frames'] += 1 * dt
        
        elif self.tween_info['flag'] is not None:
            self.tween_info['flag'] = None

            self.rect.x = self.tween_info['position'][0]
            self.rect.y = self.tween_info['position'][1]

            self.tween_info['frames'] = 0
            self.tween_info['frames_max'] = 0

            if self.tween_info['on_finished'] is not None:
                self.tween_info['on_finished']()
                self.tween_info['on_finished'] = None

        if self.hovering:
            if self.draw.DRAW_SPECIAL:
                create_outline_edge(self, self.draw.DRAW_SPECIAL[1], scene.ui_surface, 3)
            else:
                create_outline_edge(self, (255, 255, 255), scene.ui_surface, 3)

        super().display(scene, dt)
