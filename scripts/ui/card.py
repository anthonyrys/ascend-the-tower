'''
Holds the card baseclass and subclasses.
'''

from scripts.constants import SCREEN_DIMENSIONS
from scripts.engine import Frame, Easings, create_outline_edge

from scripts.services.spritesheet_loader import load_spritesheet

from scripts.ui.text_box import TextBox

import pygame
import os

class Card(Frame):
    '''
    Used to display ability, talent and stat information.

    Variables:
        IMG_SCALE: scale factor the images.
        BASE: image of the card base.
        
        ICONS: a collection of icons for the different types of talents/abilities/stats.
        SYMBOLS: a collection of symbols to display the descriptions of the different talents/abilities.

        on_select: function that is called when the card is selected

        hover_info: information on the position and easing of the object when it is hovering.

    Methods:
        create_card(): creates a new card to display.

        on_hover_start(): called when mouse is hovering over the card.
        on_hover_end(): called when mouse has stopped hovering over the card.

        set_flag(): sets the flag variable of the card object.

        on_mouse_down(): called when the mouse is pressed.
    '''

    IMG_SCALE = 4

    BASE = None

    ICONS = {
        'talent': {},
        'ability': {},
        'stats': {}
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
        base = pygame.image.load(os.path.join('imgs', 'ui', 'card', 'card-base.png'))
        Card.BASE = pygame.transform.scale(base, (base.get_width() * Card.IMG_SCALE, base.get_height() * Card.IMG_SCALE)).convert_alpha()

        for icon in os.listdir(os.path.join('imgs', 'ui', 'card', 'talents')):
            img = pygame.image.load(os.path.join('imgs', 'ui', 'card', 'talents', icon)).convert_alpha()                 
            img = pygame.transform.scale(img, (img.get_width() * Card.IMG_SCALE, img.get_height() * Card.IMG_SCALE)).convert_alpha()
            Card.ICONS['talent'][icon.split('.')[0]] = img

        for icon in os.listdir(os.path.join('imgs', 'ui', 'card', 'abilities')):
            img = pygame.image.load(os.path.join('imgs', 'ui', 'card', 'abilities', icon)).convert_alpha()
            img = pygame.transform.scale(img, (img.get_width() * Card.IMG_SCALE, img.get_height() * Card.IMG_SCALE)).convert_alpha()
            Card.ICONS['ability'][icon.split('.')[0]] = img

        for icon in os.listdir(os.path.join('imgs', 'ui', 'card', 'stats')):
            img = pygame.image.load(os.path.join('imgs', 'ui', 'card', 'stats', icon)).convert_alpha()
            img = pygame.transform.scale(img, (img.get_width() * Card.IMG_SCALE, img.get_height() * Card.IMG_SCALE)).convert_alpha()
            Card.ICONS['stats'][icon.split('.')[0]] = img

        for symbol in os.listdir(os.path.join('imgs', 'ui', 'card', 'symbols')):
            name = symbol.split('-')[1].split('.')[0]
            for index, img in enumerate(load_spritesheet(os.path.join('imgs', 'ui', 'card', 'symbols', symbol))):
                keys = list(Card.SYMBOLS[name].keys())
                img = pygame.transform.scale(img, (img.get_width() * Card.IMG_SCALE, img.get_height() * Card.IMG_SCALE)).convert_alpha()
                Card.SYMBOLS[name][keys[index]] = img

    def __init__(self, position, img, strata, spawn):
        super().__init__(position, img, None, strata)
        self.sprite_id = 'card'

        self.on_select = None
        
        self.flag = 'init'
        self.delay_timers.append([30, lambda: self.set_flag(None), []])

        self.hover_info = {
            'x': self.rect.x,
            'y': self.rect.y - 10,

            'frames': 5,
            'easing': 'ease_out_cubic',
        }

        self.tween_information['inherited'] = False

        self.hover_rect.width = self.rect.width
        self.hover_rect.height = self.rect.height + 16

        if spawn is not None:
            if spawn == 'y':
                self.rect.y = 0 - (self.image.get_height())

            if spawn == 'x':
                self.rect.x = 0 - (self.image.get_width())

            self.set_position_tween([self.original_rect.x, self.original_rect.y], 30, 'ease_out_cubic')

    def create_card(self):
        ...

    def on_hover_start(self, scene):
        self.hovering = True
        self.set_position_tween([self.hover_info['x'], self.hover_info['y']], self.hover_info['frames'], self.hover_info['easing'])

    def on_hover_end(self, scene):
        self.hovering = False
        self.set_position_tween([self.original_rect.x, self.original_rect.y], self.hover_info['frames'], self.hover_info['easing'])

    def on_mouse_down(self, scene, event):
        self.on_hover_end(scene)

    def set_flag(self, flag):
        self.flag = flag

    def display(self, scene, dt):
        if self.tween_information['position']['frames'][0] < self.tween_information['position']['frames'][1]:
            abs_prog = self.tween_information['position']['frames'][0] / self.tween_information['position']['frames'][1]
        
            self.rect.x = self.tween_information['position']['old_position'][0] + (self.tween_information['position']['new_position'][0] - self.tween_information['position']['old_position'][0]) * self.tween_information['position']['easing_style'](abs_prog)
            self.rect.y = self.tween_information['position']['old_position'][1] + (self.tween_information['position']['new_position'][1] - self.tween_information['position']['old_position'][1]) * self.tween_information['position']['easing_style'](abs_prog)

            self.tween_information['position']['frames'][0] += 1 * dt

        if self.tween_information['alpha']['frames'][0] < self.tween_information['alpha']['frames'][1]:
            abs_prog = self.tween_information['alpha']['frames'][0] / self.tween_information['alpha']['frames'][1]
        
            self.image.set_alpha(self.tween_information['alpha']['old_alpha'] + (self.tween_information['alpha']['new_alpha'] - self.tween_information['alpha']['old_alpha']) * self.tween_information['alpha']['easing_style'](abs_prog))
            
            self.tween_information['alpha']['frames'][0] += 1 * dt

        if self.hovering:
            create_outline_edge(self, (255, 255, 255), scene.ui_surface, 3)

        super().display(scene, dt)

class StandardCard(Card):
    def __init__(self, position, draw, spawn=None):
        self.draw = draw
        self.cards = None
        self.info = draw.fetch()

        super().__init__(position, self.create_card(), 3, spawn)
        self.secondary_sprite_id = 'standard_card'

        self.hover_texts = {}

        self.hover_texts['name'] = TextBox((0, self.original_rect.bottom + 50), self.draw.DESCRIPTION['name'], color=(255, 255, 255))
        self.hover_texts['name'].rect.x = (SCREEN_DIMENSIONS[0] * .5) - (self.hover_texts['name'].image.get_width() * .5)
    
        if draw.DRAW_SPECIAL:
            self.hover_texts['special'] = TextBox((0, self.original_rect.bottom + 100), draw.DRAW_SPECIAL[0], size=.5, color=draw.DRAW_SPECIAL[1])
            self.hover_texts['special'].rect.x = (SCREEN_DIMENSIONS[0] * .5) - (self.hover_texts['special'].image.get_width() * .5)

            self.hover_texts['description'] = TextBox((0, self.original_rect.bottom + 140), self.draw.DESCRIPTION['description'], size=.5, color=(255, 255, 255))
            self.hover_texts['description'].rect.x = (SCREEN_DIMENSIONS[0] * .5) - (self.hover_texts['description'].image.get_width() * .5)

        else:
            self.hover_texts['description'] = TextBox((0, self.original_rect.bottom + 110), self.draw.DESCRIPTION['description'], size=.5, color=(255, 255, 255))
            self.hover_texts['description'].rect.x = (SCREEN_DIMENSIONS[0] * .5) - (self.hover_texts['description'].image.get_width() * .5)

    def create_card(self):
        img = self.BASE.copy()
    
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
        if self.flag is not None:
            return
        
        super().on_hover_start(scene)
        scene.add_sprites(list(self.hover_texts.values()))

    def on_hover_end(self, scene):
        if self.flag is not None:
            return
        
        super().on_hover_end(scene)
        scene.del_sprites(list(self.hover_texts.values()))

    def on_mouse_down(self, scene, event):
        if not self.hovering:
            return
        
        if event != 1:
            return

        if self.flag is not None:
            return

        super().on_mouse_down(scene, event)
        self.on_select(self, self.cards, self.flavor_text)

class StatCard(Card):
    def __init__(self, position, stat, spawn=None):
        self.stat = stat
        self.cards = None

        super().__init__(position, self.create_card(), 3, spawn)
        self.secondary_sprite_id = 'stat_card'
    
        self.hover_texts = {}

        self.hover_texts['name'] = TextBox((0, self.original_rect.bottom + 50), self.stat['name'], color=(255, 255, 255))
        self.hover_texts['name'].rect.x = (SCREEN_DIMENSIONS[0] * .5) - (self.hover_texts['name'].image.get_width() * .5)

        self.hover_texts['description'] = TextBox((0, self.original_rect.bottom + 110), self.stat['description'], size=.5, color=(255, 255, 255))
        self.hover_texts['description'].rect.x = (SCREEN_DIMENSIONS[0] * .5) - (self.hover_texts['description'].image.get_width() * .5)

    def create_card(self):
        img = self.BASE.copy()
        
        icon = None
        icon_name = None

        icon_name = self.stat['name'].lower()
        if self.stat['name'].lower() not in Card.ICONS['stats']:
            icon_name = 'default'

        icon = Card.ICONS['stats'][icon_name].copy()
        icon = pygame.transform.scale(icon, (icon.get_width() * 1.2, icon.get_height() * 1.2)).convert_alpha()

        img.blit(icon, (icon.get_rect(center = (img.get_width() * .5, img.get_height() * .5))))

        return img
    
    def on_hover_start(self, scene):
        if self.flag is not None:
            return
        
        super().on_hover_start(scene)
        scene.add_sprites(list(self.hover_texts.values()))

    def on_hover_end(self, scene):
        if self.flag is not None:
            return
        
        super().on_hover_end(scene)
        scene.del_sprites(list(self.hover_texts.values()))

    def on_mouse_down(self, scene, event):
        if not self.hovering:
            return
        
        if event != 1:
            return

        if self.flag is not None:
            return

        super().on_mouse_down(scene, event)
        self.on_select(self, self.cards, self.flavor_text)
