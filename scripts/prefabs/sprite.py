from scripts.utils.bezier import get_bezier_point

import pygame

class Sprite(pygame.sprite.Sprite):
    def __init__(self, position, img, dimensions, strata, alpha=None):
        pygame.sprite.Sprite.__init__(self)
        self.sprite_id = None
        self.secondary_sprite_id = None

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

        self.collisions = []
        self.collision_ignore = []

        self.previous_true_position = [0, 0]
        self.previous_center_position = [0, 0]

        self.delay_timers = []

        self.bezier_info = {
            'inherited': True,

            'x': {
                'p_0': [0, 0],
                'p_1': [0, 0],
                'f': [0, 0],
                'b': None
            },

            'y': {
                'p_0': [0, 0],
                'p_1': [0, 0],
                'f': [0, 0],
                'b': None
            },

            'alpha': {
                'a_0': 0,
                'a_1': 0,
                'f': [0, 0],
                'b': None
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

    def set_x_bezier(self, position, frames, bezier):
        self.bezier_info['x']['p_0'] = self.rect.x
        self.bezier_info['x']['p_1'] = position
        self.bezier_info['x']['f'] = [0, frames]
        self.bezier_info['x']['b'] = bezier

    def set_y_bezier(self, position, frames, bezier):
        self.bezier_info['y']['p_0'] = self.rect.y
        self.bezier_info['y']['p_1'] = position
        self.bezier_info['y']['f'] = [0, frames]
        self.bezier_info['y']['b'] = bezier

    def set_alpha_bezier(self, alpha, frames, bezier):
        self.bezier_info['alpha']['a_0'] = self.image.get_alpha()
        self.bezier_info['alpha']['a_1'] = alpha
        self.bezier_info['alpha']['f'] = [0, frames]
        self.bezier_info['alpha']['b'] = bezier
        
    def display(self, scene, dt):
        self.previous_true_position = [self.rect.x, self.rect.y]
        self.previous_center_position = [self.rect.centerx, self.rect.centery]

        if self.bezier_info['inherited']:
            if self.bezier_info['x']['f'][0] < self.bezier_info['x']['f'][1]:
                x_info = self.bezier_info['x']
                self.rect.x = x_info['p_0'] + (x_info['p_1'] - x_info['p_0']) * get_bezier_point(x_info['f'][0] / x_info['f'][1], *x_info['b'])

                self.bezier_info['x']['f'][0] += 1 * dt

            if self.bezier_info['y']['f'][0] < self.bezier_info['y']['f'][1]:
                y_info = self.bezier_info['y']
                self.rect.y = y_info['p_0'] + (y_info['p_1'] - y_info['p_0']) * get_bezier_point(y_info['f'][0] / y_info['f'][1], *y_info['b'])

                self.bezier_info['y']['f'][0] += 1 * dt

            if self.bezier_info['alpha']['f'][0] < self.bezier_info['alpha']['f'][1]:
                alpha_info = self.bezier_info['alpha']
                alpha = alpha_info['a_0'] + (alpha_info['a_1'] - alpha_info['a_0']) * get_bezier_point(alpha_info['f'][0] / alpha_info['f'][1], *alpha_info['b'])

                self.image.set_alpha(alpha)

                self.bezier_info['alpha']['f'][0] += 1 * dt

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
