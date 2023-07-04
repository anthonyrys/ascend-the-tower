from scripts.utils.easings import Easings

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
