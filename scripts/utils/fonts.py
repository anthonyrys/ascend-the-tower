from scripts.services import load_spritesheet

import os

class Fonts:
    FONT_PATH = os.path.join('imgs', 'ui', 'fonts')

    FONT_KEYS = [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.', ':', ',', ';', '\'', '\"', '(', '!', '?', ')', '+', '-', '*', '/', '=' 
    ]

    fonts = {
        'default': {
            'info': {
                'key_spacing': [10, 32],
                'key_padding': 5,

                'key_specials': {
                    'g': 11, 
                    'p': 11, 
                    'q': 11, 
                    'y': 11,

                    ':': -4
                }
            },

            'letters': {}
        }
    }
    
    # Splits the image into seperate pygame surfaces to use
    def init():
        for font_file in os.listdir(Fonts.FONT_PATH):
            name = font_file.split('.')[0]

            imgs = load_spritesheet(os.path.join(Fonts.FONT_PATH, font_file))

            for index, key in enumerate(Fonts.FONT_KEYS):
                Fonts.fonts[name]['letters'][key] = imgs[index]
            