from scripts.ui.frame import Frame

from scripts.tools.fonts import Fonts

import pygame

class TextBox(Frame):
    @staticmethod
    def create_text_line(font, text, size=.5, color=(255, 255, 255)):
        text = str(text).lower()
        
        surf_size = [0, 0]
        imgs = []

        for letter in text:
            img = None
            if letter == ' ':
                img = pygame.Surface((Fonts.fonts[font]['info']['key_spacing'][0], Fonts.fonts[font]['info']['key_spacing'][1])).convert_alpha()
                img.set_colorkey((0, 0, 0))

            else:
                img = Fonts.fonts[font]['letters'][letter].copy()        

            surf_size[0] += img.get_width() + Fonts.fonts[font]['info']['key_padding']
            if img.get_height() > surf_size[1]:
                surf_size[1] += img.get_height() * 2

            img = pygame.transform.scale(img, (img.get_width() * size, img.get_height() * size)).convert_alpha()
            img = pygame.mask.from_surface(img).to_surface(
                setcolor=color,
                unsetcolor=(0, 0, 0)
            ).convert_alpha()

            imgs.append(img)

        surf = pygame.Surface((surf_size[0] * size, surf_size[1] * size)).convert_alpha()
        surf.set_colorkey((0, 0, 0))

        x = 0
        for img, letter in zip(imgs, text):
            if letter in Fonts.fonts[font]['info']['key_specials'].keys():
                surf.blit(img, (x, (Fonts.fonts[font]['info']['key_specials'][letter] * size)))
                x += img.get_width() + (Fonts.fonts[font]['info']['key_padding'] * size)
                continue

            surf.blit(img, (x, 0))
            x += img.get_width() + (Fonts.fonts[font]['info']['key_padding'] * size)

        return surf

    def __init__(self, position, text, color=(255, 255, 255), size=1.0, font='default', center=True, text_width=40):
        new_text = ''
        char_count = 0
        for char in str(text):
            new_text += char
            char_count += 1

            if char == ' ' and char_count >= text_width:
                new_text += '|'
                char_count = 0

        self.color = color
        self.size = size
        self.font = font

        self.texts = new_text.split('|')
        self.lines = []

        img_size = [0, 0]
        for txt in self.texts:
            surf = self.create_text_line(self.font, txt, size=self.size, color=self.color)
                    
            img_size[1] += surf.get_height() 
            if surf.get_width() > img_size[0]:
                img_size[0] = surf.get_width()

            self.lines.append(surf)

        img = pygame.Surface((img_size[0], img_size[1])).convert_alpha()
        img.set_colorkey((0, 0, 0))

        y = 0
        for line in self.lines:
            x = ((img.get_width() * .5) - (line.get_width() * .5)) if center else 0
            img.blit(line, (x, y))
            
            y += line.get_height()

        super().__init__(position, img, None, 3)
        self.sprite_id = 'text_box'
