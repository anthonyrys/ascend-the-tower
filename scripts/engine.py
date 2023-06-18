'''
Holds all of the general classes and methods used throughout the game.
'''

from scripts.constants import SCREEN_DIMENSIONS

from scripts.services.spritesheet_loader import load_spritesheet

import pygame
import random
import math
import os

class Easings:
    '''
    Contains easing methods for sprites.
    '''

    @staticmethod
    def ease_in_sine(abs_prog):
        return 1 - math.cos((abs_prog * math.pi) / 2)

    @staticmethod
    def ease_in_cubic(abs_prog):
        return abs_prog * abs_prog * abs_prog

    @staticmethod
    def ease_in_quint(abs_prog):
        return abs_prog * abs_prog * abs_prog * abs_prog

    @staticmethod
    def ease_in_cir(abs_prog):
        return 1 - math.sqrt(1 - math.pow(abs_prog, 2))

    @staticmethod
    def ease_out_sine(abs_prog):
        return math.sin((abs_prog * math.pi) / 2)

    @staticmethod
    def ease_out_cubic(abs_prog):
        return 1 - math.pow(1 - abs_prog, 3)

    @staticmethod
    def ease_out_quint(abs_prog):
        return 1 - math.pow(1 - abs_prog, 5)

    @staticmethod
    def ease_out_cir(abs_prog):
        return math.sqrt(1 - math.pow(abs_prog - 1, 2))

    @staticmethod
    def custom_position_particle_fx(abs_prog):
        return 1 - pow(1 - abs_prog, 4)

class Fonts:
    '''
    Custom font rendering; Uses image spritesheets.
    '''

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

class Inputs:
    '''
    Custom input system simplify keybinding.
    '''

    KEYBINDS = {
        'left': [pygame.K_a, pygame.K_LEFT],
        'right': [pygame.K_d, pygame.K_RIGHT],
        'down': [pygame.K_s, pygame.K_DOWN],
        'jump': [pygame.K_w, pygame.K_SPACE, pygame.K_UP],

        'ability_1': [pygame.K_1],
        'ability_2': [pygame.K_2],

        'interact': [pygame.K_f]
    }

    MOVEMENT = ['left', 'right', 'down', 'jump']

    pressed = {}

    def init():
        for keybind in Inputs.KEYBINDS.keys():
            Inputs.pressed[keybind] = False

    def get_input_general(input_list):
        for x in input_list:
            if Inputs.pressed[x]:
                return True
            
        return False

    def get_keys_pressed():
        keys = pygame.key.get_pressed()

        for action in Inputs.pressed.keys():
            Inputs.pressed[action] = False

            if not isinstance(Inputs.KEYBINDS[action], list):
                Inputs.pressed[action] = keys[Inputs.KEYBINDS[action]]
                continue

            for val in Inputs.KEYBINDS[action]:
                if not keys[val]:
                    continue

                Inputs.pressed[action] = keys[val]
                break

class CameraTemplate:
    '''
    Template class for how camera subclasses should generally behave.
    '''

    def __init__(self, focus):
        self.focus = focus
        self.offset = [0, 0]
        self.zoom = 1

        self.camera_shake_info = {
            'frames': 0,
            'max_frames': 0,
            'intensity': 10
        }

        self.camera_tween_info = {
            'frames': 0,
            'max_frames': 0,
            'start_pos': None
        }

    def set_camera_shake(self, frames, intensity=10):
        self.camera_shake_info['frames'] = frames
        self.camera_shake_info['max_frames'] = frames
        self.camera_shake_info['intensity'] = intensity

    def set_camera_tween(self, frames):
        self.camera_tween_info['frames'] = 0
        self.camera_tween_info['max_frames'] = frames
        self.camera_tween_info['start_pos'] = (self.box.topleft[0] - self.box_dimensions[0], self.box.topleft[1] - self.box_dimensions[1])

class BoxCamera(CameraTemplate):
    '''
    Camera used for the main game loop.
    '''

    def __init__(self, focus):
        super().__init__(focus)

        self.box_dimensions = (555, 265)
        self.box = pygame.Rect(
            self.box_dimensions[0],
            self.box_dimensions[1],

            SCREEN_DIMENSIONS[0] - (self.box_dimensions[0] * 2),
            SCREEN_DIMENSIONS[1] - (self.box_dimensions[1] * 2)
        )

    def update(self, dt):
        camera_shake = [0, 0]
        if self.camera_shake_info['frames'] > 0:
            abs_prog = self.camera_shake_info['frames'] / self.camera_shake_info['max_frames']
            intensity = round((self.camera_shake_info['intensity']) * Easings.ease_in_sine(abs_prog))

            camera_shake[0] = random.randint(-intensity, intensity)
            camera_shake[1] = random.randint(-intensity, intensity)

            self.camera_shake_info['frames'] -= 1 * dt

        if self.focus.rect.left < self.box.left:
            self.box.left = self.focus.rect.left

        elif self.focus.rect.right > self.box.right:
            self.box.right = self.focus.rect.right

        if self.focus.rect.bottom > self.box.bottom:
            self.box.bottom = self.focus.rect.bottom

        elif self.focus.rect.top < self.box.top:
            self.box.top = self.focus.rect.top
            
        offset = [
            self.box[0] - self.box_dimensions[0] + camera_shake[0], 
            self.box[1] - self.box_dimensions[1] + camera_shake[1]
        ]

        if self.camera_tween_info['frames'] < self.camera_tween_info['max_frames']:
            abs_prog = self.camera_tween_info['frames'] / self.camera_tween_info['max_frames']

            tweened_offset = [
                self.camera_tween_info['start_pos'][0] + ((offset[0] - self.camera_tween_info['start_pos'][0]) * Easings.ease_out_quint(abs_prog)),
                self.camera_tween_info['start_pos'][1] + ((offset[1] - self.camera_tween_info['start_pos'][1]) * Easings.ease_out_quint(abs_prog)),
            ]

            self.camera_tween_info['frames'] += 1 * dt

            self.offset = tweened_offset
            return tweened_offset

        else:
            self.offset = offset
            return offset

class Entity(pygame.sprite.Sprite):
    '''
    General sprite class used for sprites rendered to the entity surface.
    '''

    def __init__(self, position, img, dimensions, strata, alpha=None):
        pygame.sprite.Sprite.__init__(self)
        self.sprite_id = None
        self.secondary_sprite_id = None

        self.active = True
        self.strata = strata

        self.uses_ui_surface = False

        if isinstance(img, tuple):
            self.image = pygame.Surface(dimensions).convert_alpha()
            self.image.set_colorkey((0, 0, 0))
            
            self.image.fill(img)

            self.original_image = pygame.Surface(dimensions).convert_alpha()
            self.original_image.set_colorkey((0, 0, 0))
            
            self.original_image.fill(img)

        else:
            self.image = img
            self.original_image = img

        if alpha:
            self.image.set_alpha(alpha)

        self.rect = self.image.get_bounding_rect()
        self.rect.x, self.rect.y = position
        self.rect_offset = [0, 0]

        self.original_position = position
        self.original_rect = self.image.get_bounding_rect()
        self.original_rect.x, self.original_rect.y = position

        self.collide_points = {
            'top': False, 
            'bottom': False, 
            'left': False, 
            'right': False
        }

        self.glow = {
            'active': False,
            'size': 1.1,
            'intensity': .25
        }

        self.collisions = []
        self.collision_ignore = []

        self.velocity = [0, 0]
        self.previous_true_position = [0, 0]
        self.previous_center_position = [0, 0]

        self.delay_timers = []

        self.tween_information = {
            'inherited': True,

            'position': {
                'old_position': [0, 0],
                'new_position': [0, 0],
                'frames': [0, 0],
                'easing_style': None
            },

            'alpha': {
                'old_alpha': 0,
                'new_alpha': 0,
                'frames': [0, 0],
                'easing_style': None
            }
        }

    @property
    def mask(self):
        return pygame.mask.from_surface(self.image)
    
    @property
    def true_position(self):
        return [self.rect.x, self.rect.y]

    @property
    def center_position(self):
        return [self.rect.centerx, self.rect.centery]

    def set_position_tween(self, position, frames, easing_style):
        self.tween_information['position']['old_position'] = self.true_position
        self.tween_information['position']['new_position'] = position
        self.tween_information['position']['frames'] = [0, frames]

        if not hasattr(Easings, easing_style):
            self.tween_information['position']['easing_style'] = getattr(Easings, 'ease_out_sine')
            return

        self.tween_information['position']['easing_style'] = getattr(Easings, easing_style)

    def set_alpha_tween(self, alpha, frames, easing_style):
        self.tween_information['alpha']['old_alpha'] = self.image.get_alpha()
        self.tween_information['alpha']['new_alpha'] = alpha
        self.tween_information['alpha']['frames'] = [0, frames]

        if not hasattr(Easings, easing_style):
            self.tween_information['alpha']['easing_style'] = getattr(Easings, 'ease_out_sine')
            return

        self.tween_information['alpha']['easing_style'] = getattr(Easings, easing_style)
        
    def display(self, scene, dt):
        self.previous_true_position = [self.rect.x, self.rect.y]
        self.previous_center_position = [self.rect.centerx, self.rect.centery]

        if self.tween_information['inherited']:
            if self.tween_information['position']['frames'][0] < self.tween_information['position']['frames'][1]:
                abs_prog = self.tween_information['position']['frames'][0] / self.tween_information['position']['frames'][1]
            
                self.rect.x = self.tween_information['position']['old_position'][0] + (self.tween_information['position']['new_position'][0] - self.tween_information['position']['old_position'][0]) * self.tween_information['position']['easing_style'](abs_prog)
                self.rect.y = self.tween_information['position']['old_position'][1] + (self.tween_information['position']['new_position'][1] - self.tween_information['position']['old_position'][1]) * self.tween_information['position']['easing_style'](abs_prog)

                self.tween_information['position']['frames'][0] += 1 * dt

            if self.tween_information['alpha']['frames'][0] < self.tween_information['alpha']['frames'][1]:
                abs_prog = self.tween_information['alpha']['frames'][0] / self.tween_information['alpha']['frames'][1]
            
                self.image.set_alpha(self.tween_information['alpha']['old_alpha'] + (self.tween_information['alpha']['new_alpha'] - self.tween_information['alpha']['old_alpha']) * self.tween_information['alpha']['easing_style'](abs_prog))
                
                self.tween_information['alpha']['frames'][0] += 1 * dt

        if self.glow['active']:
            image = pygame.transform.scale(self.image, (self.image.get_width() * self.glow['size'], self.image.get_height() * self.glow['size']))
            image.set_alpha(self.image.get_alpha() * self.glow['intensity'])

            rect = image.get_rect()
            rect.center = [
                self.rect.centerx - self.rect_offset[0],
                self.rect.centery - self.rect_offset[1]
            ]

            scene.entity_surface.blit(
                image, 
                rect
            )

        remove_list = []
        for i in range(len(self.delay_timers)):
            if self.delay_timers[i][0] <= 0:
                continue
            
            self.delay_timers[i][0] -= 1

            if self.delay_timers[i][0] <= 0 and self.delay_timers[i][1]:
                self.delay_timers[i][1](*self.delay_timers[i][2])
                remove_list.append(self.delay_timers[i])

        for element in remove_list:
            self.delay_timers.remove(element)

        if self.uses_ui_surface:
            scene.ui_surface.blit(
                self.image, 
                (self.rect.x - self.rect_offset[0], self.rect.y - self.rect_offset[1]),
            )
            
        else:
            scene.entity_surface.blit(
                self.image, 
                (self.rect.x - self.rect_offset[0], self.rect.y - self.rect_offset[1]),
            )

class Frame(pygame.sprite.Sprite):
    '''
    General sprite class used for sprites rendered to the ui surface.
    '''

    def __init__(self, position, img, dimensions, strata, alpha=None):
        self.sprite_id = None
        self.secondary_sprite_id = None

        pygame.sprite.Sprite.__init__(self)
        self.active = True
        self.strata = strata

        self.uses_entity_surface = False
        
        self.hovering = False
        self.pressed = False

        if isinstance(img, tuple):
            self.image = pygame.Surface(dimensions).convert_alpha()
            self.image.set_colorkey((0, 0, 0))
            
            self.image.fill(img)

            self.original_image = pygame.Surface(dimensions).convert_alpha()
            self.original_image.set_colorkey((0, 0, 0))
            
            self.original_image.fill(img)

        else:
            self.image = img
            self.original_image = img

        if alpha:
            self.image.set_alpha(alpha)

        self.rect = self.image.get_bounding_rect()
        self.rect.x, self.rect.y = position
        self.rect_offset = [0, 0]
        
        self.hover_rect = pygame.Rect(self.rect.x, self.rect.y, 0, 0)
        
        self.original_rect = self.image.get_bounding_rect()
        self.original_rect.x, self.original_rect.y = position

        self.global_offset = (0, 0)

        self.delay_timers = []

        self.tween_information = {
            'inherited': True,

            'position': {
                'old_position': [0, 0],
                'new_position': [0, 0],
                'frames': [0, 0],
                'easing_style': None
            },

            'alpha': {
                'old_alpha': 0,
                'new_alpha': 0,
                'frames': [0, 0],
                'easing_style': None
            }
        }

    @property
    def mask(self):
        return pygame.mask.from_surface(self.image)

    @property
    def true_position(self):
        return [self.rect.x, self.rect.y]

    @property
    def center_position(self):
        return [self.rect.centerx, self.rect.centery]

    def set_position_tween(self, position, frames, easing_style):
        self.tween_information['position']['old_position'] = self.true_position
        self.tween_information['position']['new_position'] = position
        self.tween_information['position']['frames'] = [0, frames]

        if not hasattr(Easings, easing_style):
            self.tween_information['position']['easing_style'] = getattr(Easings, 'ease_out_sine')
            return

        self.tween_information['position']['easing_style'] = getattr(Easings, easing_style)

    def set_alpha_tween(self, alpha, frames, easing_style):
        self.tween_information['alpha']['old_alpha'] = self.image.get_alpha()
        self.tween_information['alpha']['new_alpha'] = alpha
        self.tween_information['alpha']['frames'] = [0, frames]

        if not hasattr(Easings, easing_style):
            self.tween_information['alpha']['easing_style'] = getattr(Easings, 'ease_out_sine')
            return

        self.tween_information['alpha']['easing_style'] = getattr(Easings, easing_style)

    def display(self, scene, dt):    
        if self.tween_information['inherited']:
            if self.tween_information['position']['frames'][0] < self.tween_information['position']['frames'][1]:
                abs_prog = self.tween_information['position']['frames'][0] / self.tween_information['position']['frames'][1]
            
                self.rect.x = self.tween_information['position']['old_position'][0] + (self.tween_information['position']['new_position'][0] - self.tween_information['position']['old_position'][0]) * self.tween_information['position']['easing_style'](abs_prog)
                self.rect.y = self.tween_information['position']['old_position'][1] + (self.tween_information['position']['new_position'][1] - self.tween_information['position']['old_position'][1]) * self.tween_information['position']['easing_style'](abs_prog)

                self.tween_information['position']['frames'][0] += 1 * dt

            if self.tween_information['alpha']['frames'][0] < self.tween_information['alpha']['frames'][1]:
                abs_prog = self.tween_information['alpha']['frames'][0] / self.tween_information['alpha']['frames'][1]
            
                self.image.set_alpha(self.tween_information['alpha']['old_alpha'] + (self.tween_information['alpha']['new_alpha'] - self.tween_information['alpha']['old_alpha']) * self.tween_information['alpha']['easing_style'](abs_prog))
                
                self.tween_information['alpha']['frames'][0] += 1 * dt

        self.hover_rect.x = self.rect.x
        self.hover_rect.y = self.rect.y

        remove_list = []
        for i in range(len(self.delay_timers)):
            if self.delay_timers[i][0] <= 0:
                continue
            
            self.delay_timers[i][0] -= 1

            if self.delay_timers[i][0] <= 0 and self.delay_timers[i][1]:
                self.delay_timers[i][1](*self.delay_timers[i][2])
                remove_list.append(self.delay_timers[i])

        for element in remove_list:
            self.delay_timers.remove(element)

        if self.uses_entity_surface:
            scene.entity_surface.blit(
                self.image, 
                (self.rect.x + self.global_offset[0], self.rect.y + self.global_offset[1]),
            )
            
        else:
            scene.ui_surface.blit(
                self.image, 
                (self.rect.x + self.global_offset[0], self.rect.y + self.global_offset[1]),
            )

    def on_del_sprite(self, scene, time):
        self.delay_timers.append([time, lambda: scene.del_sprites(self), []])
        
    def on_hover_start(self, scene):
        ...

    def on_hover_end(self, scene):
        ...

    def on_press(self, scene):
        ...

def check_pixel_collision(primary_sprite, secondary_sprite):
    collision = None
    if not isinstance(secondary_sprite, pygame.sprite.Group):
        group = pygame.sprite.Group(secondary_sprite)
        collision = pygame.sprite.spritecollide(primary_sprite, group, False, pygame.sprite.collide_mask)
        group.remove(secondary_sprite)

    else:
        collision = pygame.sprite.spritecollide(primary_sprite, secondary_sprite, False, pygame.sprite.collide_mask)

    return collision

def check_line_collision(start, end, sprites):
    clipped_sprites = []

    for sprite in sprites:
        if sprite.rect.clipline(start, end):
            clipped_sprites.append([sprite, sprite.rect.clipline(start, end)])

    return clipped_sprites

def get_distance(primary_sprite, secondary_sprite):
    if isinstance(primary_sprite, pygame.sprite.Sprite) and isinstance(secondary_sprite, pygame.sprite.Sprite):
        rx = abs(secondary_sprite.rect.x - primary_sprite.rect.x)
        ry = abs(secondary_sprite.rect.y - primary_sprite.rect.y)

        return math.sqrt(((rx **2) + (ry **2)))
        
    else:
        rx = abs(secondary_sprite[0] - primary_sprite[0])
        ry = abs(secondary_sprite[1] - primary_sprite[1])

        return math.sqrt(((rx **2) + (ry **2)))  

def get_closest_sprite(primary_sprite, sprites):
    if len(sprites) == 1:
        return sprites[0]
                
    sprite_area = {}

    for sprite in sprites:
        distance = get_distance(primary_sprite, sprite)
        sprite_area[sprite] = distance

    min_value = min(sprite_area.values())
    for sprite, area in sprite_area.items():
        if area == min_value:
            return sprite

    return None

def get_sprite_colors(primary_sprite, multiplier=1):
    iteration_threshold = .1
    iterations = int((((primary_sprite.image.get_width() + primary_sprite.image.get_height()) / 2) * iteration_threshold) * multiplier)

    colors = []
    for _ in range(iterations):
        found_pixel = False
        x = 0
        y = 0

        while not found_pixel:
            x = random.randint(0, primary_sprite.image.get_width() - 1)
            y = random.randint(0, primary_sprite.image.get_height() - 1)

            found_pixel = primary_sprite.image.get_at((x, y)) != ((0, 0, 0, 0))
                
        colors.append(primary_sprite.image.get_at([x, y]))

    return colors

def create_outline_edge(sprite, color, display, size=1):
    surface = pygame.Surface(sprite.image.get_size())
    surface.set_colorkey((0, 0, 0))
    for point in sprite.mask.outline():
        surface.set_at(point, color)

    for i in range(size):
        display.blit(surface, (sprite.rect.x + sprite.rect_offset[0] - i, sprite.rect.y + sprite.rect_offset[1]))
        display.blit(surface, (sprite.rect.x + sprite.rect_offset[0] + i, sprite.rect.y + sprite.rect_offset[1]))

        display.blit(surface, (sprite.rect.x + sprite.rect_offset[0], sprite.rect.y + sprite.rect_offset[1] - i))
        display.blit(surface, (sprite.rect.x + sprite.rect_offset[0], sprite.rect.y + sprite.rect_offset[1] + i))

        display.blit(surface, (sprite.rect.x + sprite.rect_offset[0] - i, sprite.rect.y + sprite.rect_offset[1] - i))
        display.blit(surface, (sprite.rect.x + sprite.rect_offset[0] + i, sprite.rect.y + sprite.rect_offset[1] + i))

        display.blit(surface, (sprite.rect.x + sprite.rect_offset[0] - i, sprite.rect.y + sprite.rect_offset[1] + i))
        display.blit(surface, (sprite.rect.x + sprite.rect_offset[0] + i, sprite.rect.y + sprite.rect_offset[1] - i))  

def create_outline_full(sprite, color, display, size=1):
    surface = sprite.mask.to_surface(
        setcolor=color, 
        unsetcolor=(0, 0, 0, 0)
    )
    surface.set_colorkey((0, 0, 0))

    for i in range(size):
        display.blit(surface, (sprite.rect.x - sprite.rect_offset[0] - i, sprite.rect.y - sprite.rect_offset[1]))
        display.blit(surface, (sprite.rect.x - sprite.rect_offset[0] + i, sprite.rect.y - sprite.rect_offset[1]))

        display.blit(surface, (sprite.rect.x - sprite.rect_offset[0], sprite.rect.y - sprite.rect_offset[1] - i))
        display.blit(surface, (sprite.rect.x - sprite.rect_offset[0], sprite.rect.y - sprite.rect_offset[1] + i))

        display.blit(surface, (sprite.rect.x - sprite.rect_offset[0] - i, sprite.rect.y - sprite.rect_offset[1] - i))
        display.blit(surface, (sprite.rect.x - sprite.rect_offset[0] + i, sprite.rect.y - sprite.rect_offset[1] + i))

        display.blit(surface, (sprite.rect.x - sprite.rect_offset[0] - i, sprite.rect.y - sprite.rect_offset[1] + i))
        display.blit(surface, (sprite.rect.x - sprite.rect_offset[0] + i, sprite.rect.y - sprite.rect_offset[1] - i))  