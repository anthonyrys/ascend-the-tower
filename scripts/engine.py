from scripts.constants import SCREEN_DIMENSIONS

import pygame
import random
import math
import os

class Easings:
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
    FONT_PATH = os.path.join('imgs', 'ui', 'fonts')

    FONT_KEYS = [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.', ':', ',', ';', '\'', '\"', '(', '!', '?', ')', '+', '-', '*', '/', '=' 
    ]
    FONT_KEYS_SPECIAL = [
        'g', 'p', 'q', 'y', 
        '.', ':', ',', ';'
    ]

    fonts = {}
    font_offsets = {
        'default': {}
    }
    
    def init():
        for font_file in os.listdir(Fonts.FONT_PATH):
            name = font_file.split('.')[0]

            img = pygame.image.load(os.path.join(Fonts.FONT_PATH, font_file)).convert_alpha()
            img.set_colorkey((0, 0, 0))

            for key in Fonts.FONT_KEYS:
                ...

class Inputs:
    KEYBINDS = {
        'left': [pygame.K_a, pygame.K_LEFT],
        'right': [pygame.K_d, pygame.K_RIGHT],
        'down': [pygame.K_s, pygame.K_DOWN],
        'jump': [pygame.K_w, pygame.K_SPACE, pygame.K_UP],

        'ability_1': [],
        'ability_2': [],
        'ability_3': []
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
    GRAVITY = 2
    MAX_GRAVITY = 30

    def __init__(self, position, img, dimensions, strata, alpha=None):
        pygame.sprite.Sprite.__init__(self)
        self.active = True
        self.strata = strata

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

        self.gravity_info = {
            'frames': 0,
            'gravity': Entity.GRAVITY,
            'max_gravity': Entity.MAX_GRAVITY
        }

        self.collisions = []
        self.collision_ignore = []

        self.velocity = [0, 0]
        self.previous_true_position = [0, 0]
        self.previous_center_position = [0, 0]

    @property
    def mask(self):
        return pygame.mask.from_surface(self.image)
    
    @property
    def true_position(self):
        return [self.rect.x, self.rect.y]

    @property
    def center_position(self):
        return [self.rect.centerx, self.rect.centery]

    def display(self, scene, dt):
        self.previous_true_position = [self.rect.x, self.rect.y]
        self.previous_center_position = [self.rect.centerx, self.rect.centery]

        if self.gravity_info['frames'] > 0:
            self.gravity_info['frames'] -= 1 * dt

        elif self.gravity_info['frames'] <= 0:
            if self.gravity_info['gravity'] != Entity.GRAVITY or self.gravity_info['max_gravity'] != Entity.MAX_GRAVITY:
                self.gravity_info = {
                    'frames': 0,
                    'gravity': Entity.GRAVITY,
                    'max_gravity': Entity.MAX_GRAVITY
                }

        if self.glow['active']:
            image = pygame.transform.scale(self.image, (self.image.get_width() * self.glow['size'], self.image.get_height() * self.glow['size']))
            image.set_alpha(self.image.get_alpha() * self.glow['intensity'])
            
            offset = [(image.get_width() - self.image.get_width()) / 2, (image.get_height() - self.image.get_height()) / 2]

            scene.entity_surface.blit(
                image, 
                (self.rect.x - self.rect_offset[0] - offset[0], self.rect.y - self.rect_offset[1] - offset[0], 0, 0),
            )

        scene.entity_surface.blit(
            self.image, 
            (self.rect.x - self.rect_offset[0], self.rect.y - self.rect_offset[1], 0, 0),
        )

    def apply_collision_x_default(self, collidables):
        callback_collision = []

        for collidable in collidables:
            if not self.rect.colliderect(collidable.rect):
                if collidable in self.collision_ignore:
                    self.collision_ignore.remove(collidable)
                
                if collidable in self.collisions:
                    self.collisions.remove(collidable)

                continue

            if collidable in self.collision_ignore:
                continue

            if self.velocity[0] > 0:
                self.rect.right = collidable.rect.left
                self.collide_points['right'] = True

                callback_collision.append('right')

                if collidable not in self.collisions:
                    self.collisions.append(collidable)
       
                self.velocity[0] = 0

            if self.velocity[0] < 0:
                self.rect.left = collidable.rect.right
                self.collide_points['left'] = True

                if collidable not in self.collisions:
                    self.collisions.append(collidable)

                callback_collision.append('left')
                self.velocity[0] = 0

        return callback_collision

    def apply_collision_y_default(self, collidables):
        callback_collision = []

        for collidable in collidables:
            if not self.rect.colliderect(collidable.rect):
                if collidable in self.collision_ignore:
                    self.collision_ignore.remove(collidable)

                if collidable in self.collisions:
                    self.collisions.remove(collidable)
                    
                continue

            if collidable in self.collision_ignore:
                continue

            if abs(self.velocity[1]) < 0:
                return

            top = abs(self.rect.top - collidable.rect.centery)
            bottom = abs(self.rect.bottom - collidable.rect.centery)
            
            if top < bottom and collidable.special != 'floor':
                self.rect.top = collidable.rect.bottom
                self.collide_points['top'] = True

                callback_collision.append('top')

                if collidable not in self.collisions:
                    self.collisions.append(collidable)
                    
                self.velocity[1] = 0

            else:
                self.rect.bottom = collidable.rect.top
                self.collide_points['bottom'] = True

                callback_collision.append('bottom')

                if collidable not in self.collisions:
                    self.collisions.append(collidable)

                self.velocity[1] = 0

        return callback_collision  

    def apply_gravity(self, dt, multiplier=1.0):
        grav = self.gravity_info['gravity']
        max_grav = self.gravity_info['max_gravity']

        if not self.collide_points['bottom']:
            self.velocity[1] += (grav * dt if self.velocity[1] < max_grav * dt else 0) * multiplier

        else:
            if dt == 0:
                self.velocity[1] = 0

            else:
                self.velocity[1] = (grav / dt) * multiplier

    def set_gravity(self, frames, grav=None, max_grav=None):
        if grav is None:
            grav = Entity.GRAVITY

        if max_grav is None:
            max_grav = Entity.MAX_GRAVITY

        self.gravity_info['frames'] = frames
        self.gravity_info['gravity'] = grav
        self.gravity_info['max_gravity'] = max_grav

class Frame(pygame.sprite.Sprite):
    def __init__(self, position, img, dimensions, strata, alpha=None):
        pygame.sprite.Sprite.__init__(self)
        self.active = True
        self.strata = strata

        self.uses_entity_surface = False

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
        
        self.original_rect = self.image.get_bounding_rect()
        self.original_rect.x, self.original_rect.y = position

        self.global_offset = (0, 0)

    @property
    def mask(self):
        return pygame.mask.from_surface(self.image)

    def display(self, scene, dt):
        if self.uses_entity_surface:
            scene.entity_surface.blit(
                self.image, 
                (self.rect.x + self.global_offset[0], self.rect.y + self.global_offset[1], 0, 0),
            )
            
        else:
            scene.ui_surface.blit(
                self.image, 
                (self.rect.x + self.global_offset[0], self.rect.y + self.global_offset[1], 0, 0),
            )

class SpriteMethods:
    @staticmethod
    def check_pixel_collision(primary_sprite, secondary_sprite):
        collision = None
        if not isinstance(secondary_sprite, pygame.sprite.Group):
            group = pygame.sprite.Group(secondary_sprite)
            collision = pygame.sprite.spritecollide(primary_sprite, group, False, pygame.sprite.collide_mask)
            group.remove(secondary_sprite)

        else:
            collision = pygame.sprite.spritecollide(primary_sprite, secondary_sprite, False, pygame.sprite.collide_mask)

        return collision

    @staticmethod
    def check_line_collision(start, end, sprites):
        clipped_sprites = []

        for sprite in sprites:
            if sprite.rect.clipline(start, end):
                clipped_sprites.append([sprite, sprite.rect.clipline(start, end)])

        return clipped_sprites

    @staticmethod
    def get_distance(primary_sprite, secondary_sprite):
        if isinstance(primary_sprite, pygame.sprite.Sprite) and isinstance(secondary_sprite, pygame.sprite.Sprite):
            rx = abs(secondary_sprite.rect.x - primary_sprite.rect.x)
            ry = abs(secondary_sprite.rect.y - primary_sprite.rect.y)

            return math.sqrt(((rx **2) + (ry **2)))
        
        else:
            rx = abs(secondary_sprite[0] - primary_sprite[0])
            ry = abs(secondary_sprite[1] - primary_sprite[1])

            return math.sqrt(((rx **2) + (ry **2)))  

    @staticmethod
    def get_closest_sprite(primary_sprite, sprites):
        if len(sprites) == 1:
            return sprites[0]
                
        sprite_area = {}

        for sprite in sprites:
            distance = SpriteMethods.get_distance(primary_sprite, sprite)
            sprite_area[sprite] = distance

        min_value = min(sprite_area.values())
        for sprite, area in sprite_area.items():
            if area == min_value:
                return sprite

        return None

    @staticmethod
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

    @staticmethod
    def create_outline_edge(sprite, color, display, size=1):
        surface = pygame.Surface(sprite.image.get_size())
        surface.set_colorkey((0, 0, 0))
        for point in sprite.mask.outline():
            surface.set_at(point, color)

        for i in range(size):
            #display.blit(surface, (sprite.rect.x + i, sprite.rect.y))
             #display.blit(surface, (sprite.rect.x - i, sprite.rect.y))
            # display.blit(surface, (sprite.rect.x, sprite.rect.y + i))
            # display.blit(surface, (sprite.rect.x, sprite.rect.y - i))

            display.blit(surface, (sprite.rect.x - i, sprite.rect.y))
            display.blit(surface, (sprite.rect.x + i, sprite.rect.y))

            display.blit(surface, (sprite.rect.x, sprite.rect.y - i))
            display.blit(surface, (sprite.rect.x, sprite.rect.y + i))

            display.blit(surface, (sprite.rect.x - i, sprite.rect.y - i))
            display.blit(surface, (sprite.rect.x + i, sprite.rect.y + i))

            display.blit(surface, (sprite.rect.x - i, sprite.rect.y + i))
            display.blit(surface, (sprite.rect.x + i, sprite.rect.y - i))  

    @staticmethod
    def create_outline_full(sprite, color, display, size=1):
        surface = sprite.mask.to_surface(
            setcolor=color, 
            unsetcolor=(0, 0, 0, 0)
        )
        surface.set_colorkey((0, 0, 0))

        for i in range(size):
            display.blit(surface, (sprite.rect.x - i, sprite.rect.y))
            display.blit(surface, (sprite.rect.x + i, sprite.rect.y))

            display.blit(surface, (sprite.rect.x, sprite.rect.y - i))
            display.blit(surface, (sprite.rect.x, sprite.rect.y + i))

            display.blit(surface, (sprite.rect.x - i, sprite.rect.y - i))
            display.blit(surface, (sprite.rect.x + i, sprite.rect.y + i))

            display.blit(surface, (sprite.rect.x - i, sprite.rect.y + i))
            display.blit(surface, (sprite.rect.x + i, sprite.rect.y - i))  