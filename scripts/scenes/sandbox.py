from scripts.constants import SCREEN_DIMENSIONS
from scripts.engine import BoxCamera, Entity, Easings

from scripts.core_systems.talents import get_all_talents

from scripts.entities.enemy import Stelemental
from scripts.entities.player import Player
from scripts.entities.tiles import Block, Platform, Floor

from scripts.scenes.scene import Scene

from scripts.ui.info_bar import HealthBar
from scripts.ui.card import Card
from scripts.ui.text_box import TextBox

import pygame
import random
import math

class Sandbox(Scene):
    def __init__(self, surfaces, mouse, sprites=None):
        super().__init__(surfaces, mouse, sprites)

        self.player = Player((2500, 1200), 4)
        self.enemy_info = [[120, 60], [0, 3]]

        self.camera = BoxCamera(self.player)
        self.camera_offset = [0, 0]
        
        self.ui = {
            'healthbar': HealthBar(self.player),
            'temp_guide': [
                TextBox((40, SCREEN_DIMENSIONS[1] - 50), '1: draw cards', size=.5),
                TextBox((40, SCREEN_DIMENSIONS[1] - 100), '0: fullscreen', size=.5)
            ]
        }

        self.scene_fx = {
            'entity_dim': {
                'type': None, 
                'amount': 0.75,
                'frames': [0, 0],
                'easing': 'ease_out_quint'
            },

            'entity_zoom': {}
        }

        self.player.healthbar = self.ui['healthbar']
        
        self.tiles = {
            'barrier_y': [Floor((0, 1500), (255, 255, 255, 0), (250, 250), 1)],
            'barrier_x': [
                Block((250, 0), (255, 255, 255, 0), (250, 250), 1),        
                Block((4500, 0), (255, 255, 255, 0), (250, 250), 1)
            ],

            'floor': [
                Floor((0, 1500), (155, 155, 255), (5000, 25), 1)
            ],

            'blocks': [
                Block((596, 1405), (155, 155, 255), (48, 96), 5),
                Block((836, 1405), (155, 155, 255), (48, 96), 5),

                Block((3500, 1453), (155, 155, 255), (96, 48), 5), 
                Block((3750, 1405), (155, 155, 255), (96, 96), 5), 
                Block((4000, 1357), (155, 155, 255), (96, 144), 5), 

                Block((1400, 1452), (155, 155, 255), (48, 48), 5),
                Block((1600, 1404), (155, 155, 255), (48, 48), 5), 
                Block((1800, 1356), (155, 155, 255), (48, 48), 5), 
                Block((2000, 1308), (155, 155, 255), (48, 48), 5),   
                Block((2800, 1452), (155, 155, 255), (48, 48), 5), 
                Block((2600, 1404), (155, 155, 255), (48, 48), 5),
                Block((2400, 1356), (155, 155, 255), (48, 48), 5),
                Block((2200, 1308), (155, 155, 255), (48, 48), 5) 
            ],

            'platforms': [Platform((644, 1405), (125, 125, 255), (192, 8), 3)]
        }

        self.add_sprites(self.player)

        for sprite_list in self.tiles.values():
            for sprite in sprite_list:
                self.add_sprites(sprite)

        for sprite in self.ui.values():
            self.add_sprites(sprite)

    def on_key_down(self, event):
        super().on_key_down(event)

        if self.paused:
            return
        
        if event.key == pygame.key.key_code('1'):
            self.generate_cards()

    def remove_cards(self, selected_card, cards):
        for card in cards:
            card.tween_info['base_position'] = [card.original_rect.x, card.original_rect.y]
            card.tween_info['position'] = [card.rect.x, SCREEN_DIMENSIONS[1] * 1.1]

            if card == selected_card:
                card.tween_info['position'] = [card.rect.x, 0 - card.rect.height * 1.1]
                card.tween_info['on_finished'] = lambda: self.del_sprites(cards)

            card.tween_info['frames'] = 0
            card.tween_info['frames_max'] = 20
                
            card.tween_info['flag'] = 'del'

        self.player.talents.append(selected_card.draw(self, self.player))

        if selected_card.info['type'] == 'talent':
            print(f'selected card: {selected_card.draw.TALENT_ID}')
                
        elif selected_card.info['type'] == 'ability':
            print(f'selected card: {selected_card.draw.ABILITY_ID}')

        self.in_menu = False
        self.paused = False

        self.scene_fx['entity_dim']['type'] = 'out'
        self.scene_fx['entity_dim']['easing'] = 'ease_in_quint'
        self.scene_fx['entity_dim']['frames'][0] = 30
        self.scene_fx['entity_dim']['frames'][1] = 30

    def generate_cards(self, count=3):
        if count <= 0:
            return
        
        talent_exclude_list = []
        ability_exclude_list = []

        player_talents = [t.__class__ for t in self.player.talents]
        player_abilities = [t.__class__ for t in self.player.abilities.values()]

        drawables = []
        draws = []
        draw_count = count

        for talent in get_all_talents():
            if talent.TALENT_ID in talent_exclude_list:
                continue

            if talent in player_talents:
                continue

            if not talent.check_draw_condition(self.player):
                continue

            drawables.append(talent)    

        if len(drawables) < draw_count:
            return
            
        self.in_menu = True
        self.paused = True

        self.scene_fx['entity_dim']['easing'] = 'ease_out_quint'
        self.scene_fx['entity_dim']['type'] = 'in'
        self.scene_fx['entity_dim']['frames'][1] = 30

        draws = random.sample(drawables, k=draw_count)
        cards = []

        x = (SCREEN_DIMENSIONS[0] * .5) - 80
        y = (SCREEN_DIMENSIONS[1] * .5) - 100

        i = None
        if draw_count % 2 == 0:
            i = -(math.floor(draw_count / 2) - .5)
        else:
            i = -math.floor(draw_count / 2)

        for draw in draws:
            cards.append(Card((x + (i * 200), y), draw, spawn='y'))
            i += 1

        for card in cards:
            card.drawed_cards = cards
            card.on_select = self.remove_cards

        self.add_sprites(cards)

    def display(self, screen, clock, dt):
        if self.dt_info['frames'] > 0:
            dt *= self.dt_info['multiplier']
            self.dt_info['frames'] -= 1

        dt = 3 if dt > 3 else dt
        dt = round(dt, 1)

        entity_dt = dt
        if self.paused:
            entity_dt = 0
        
        entity_view = pygame.Rect(
            self.camera_offset[0] - self.view.width * .5, self.camera_offset[1] - self.view.height * .5, 
            self.view.width * 2, self.view.height * 2
        )

        self.background_surface.fill((0, 0, 0, 255), self.view)
        self.entity_surface.fill((0, 0, 0, 0), entity_view)
        self.ui_surface.fill((0, 0, 0, 0), self.view)

        self.enemy_info[1][0] = len([s for s in self.sprites if s.secondary_sprite_id == 'stelemental'])
        if self.enemy_info[0][0] >= self.enemy_info[0][1]:
            self.enemy_info[0][0] = 0

            if self.enemy_info[1][0] < self.enemy_info[1][1]:
                self.add_sprites(Stelemental((random.randint(2000, 2500), random.randint(1000, 1600)), 6))

        self.enemy_info[0][0] += 1 * entity_dt

        display_order = self.sort_sprites(self.sprites)
        for _, v in sorted(display_order.items()):
            for sprite in v: 
                if not sprite.active:
                    continue

                if isinstance(sprite, Entity):
                    sprite.display(self, entity_dt)
                    continue

                sprite.display(self, dt)

        for barrier in self.tiles['barrier_y']:
            barrier.rect.centerx = self.player.rect.centerx

        for barrier in self.tiles['barrier_x']:
            barrier.rect.centery = self.player.rect.centery

        self.camera_offset = self.camera.update(dt)
        self.mouse.display(self)

        entity_display = pygame.Surface(SCREEN_DIMENSIONS).convert_alpha()
        entity_display.blit(self.entity_surface, (-self.camera_offset[0], -self.camera_offset[1]))
        
        if self.scene_fx['entity_dim']['type']:
            abs_prog = self.scene_fx['entity_dim']['frames'][0] / self.scene_fx['entity_dim']['frames'][1]
            img = pygame.Surface(SCREEN_DIMENSIONS)
            img.fill((0, 0, 0))

            if self.scene_fx['entity_dim']['type'] == 'in':
                img.set_alpha(255 * (self.scene_fx['entity_dim']['amount'] * getattr(Easings, self.scene_fx['entity_dim']['easing'])(abs_prog)))
                if self.scene_fx['entity_dim']['frames'][0] < self.scene_fx['entity_dim']['frames'][1]:
                    self.scene_fx['entity_dim']['frames'][0] += 1

            elif self.scene_fx['entity_dim']['type'] == 'out':
                img.set_alpha(255 * (self.scene_fx['entity_dim']['amount'] * getattr(Easings, self.scene_fx['entity_dim']['easing'])(abs_prog)))
                if self.scene_fx['entity_dim']['frames'][0] > 0:
                    self.scene_fx['entity_dim']['frames'][0] -= 1
                else:
                    self.scene_fx['entity_dim']['type'] = None

            entity_display.blit(img, (0, 0))

        screen.blit(self.background_surface, (0, 0))
        screen.blit(entity_display, (entity_display.get_rect(center=screen.get_rect().center)))
        screen.blit(self.ui_surface, (0, 0))

        self.frame_count_raw += 1 * dt
        self.frame_count = round(self.frame_count_raw)
