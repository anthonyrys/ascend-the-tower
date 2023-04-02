from scripts.constants import SCREEN_DIMENSIONS
from scripts.engine import BoxCamera, Entity

from scripts.core_systems.talents import get_all_talents

from scripts.entities.enemy import Stelemental
from scripts.entities.player import Player
from scripts.entities.tiles import Block, Platform, Ramp, Floor

from scripts.scenes.scene import Scene

from scripts.ui.info_bar import HealthBar
from scripts.ui.card import Card

import pygame
import random
import math

class Sandbox(Scene):
    def __init__(self, surfaces, mouse, sprites=None):
        super().__init__(surfaces, mouse, sprites)

        self.player = Player((615, 1200), 4)
        self.enemy_info = [[120, 60], [0, 3]]

        self.camera = BoxCamera(self.player)
        self.camera_offset = [0, 0]
        
        self.ui = {
            'healthbar': HealthBar(self.player)
        }

        self.player.healthbar = self.ui['healthbar']

        self.tiles = {
            'floors': [Floor((0, 1500), (155, 155, 255), (10000, 100), 5)],

            'walls': [
                Block((-20, 0), (155, 155, 255), (20, 1500), 5),        
                Block((10000, 0), (155, 155, 255), (20, 1500), 5)
            ],

            'blocks': [
                Block((596, 1405), (155, 155, 255), (48, 96), 5),
                Block((836, 1405), (155, 155, 255), (48, 96), 5),
                Block((196, 1453), (155, 155, 255), (96, 48), 5), 
                Block((1400, 1452), (155, 155, 255), (48, 48), 5),
                Block((1600, 1404), (155, 155, 255), (48, 48), 5), 
                Block((1800, 1356), (155, 155, 255), (48, 48), 5), 
                Block((2000, 1308), (155, 155, 255), (48, 48), 5),   
                Block((2800, 1452), (155, 155, 255), (48, 48), 5), 
                Block((2600, 1404), (155, 155, 255), (48, 48), 5),
                Block((2400, 1356), (155, 155, 255), (48, 48), 5),
                Block((2200, 1308), (155, 155, 255), (48, 48), 5) 
            ],

            'ramps': [
                Ramp((500, 1405), 0, 'right', (155, 155, 255), 5),
                Ramp((884, 1405), 0, 'left', (155, 155, 255), 5),
                Ramp((100, 1405), 1, 'right', (155, 155, 255), 5),
                Ramp((292, 1405), 1, 'left', (155, 155, 255), 5)
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
        
        if event.key == pygame.key.key_code('`'):
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

    def generate_cards(self, count=3):
        if count <= 0:
            return
        
        talent_exclude_list = []
        ability_exclude_list = []

        player_talents = [t.__class__ for t in self.player.talents]
        player_abilities = [t.__class__ for t in list(self.player.abilities.values())]

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
                self.add_sprites(Stelemental((random.randint(800, 1400), random.randint(1000, 1600)), 6))

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

        self.camera_offset = self.camera.update(dt)
        self.mouse.display(self)

        screen.blit(self.background_surface, (0, 0))
        screen.blit(self.entity_surface, (-self.camera_offset[0], -self.camera_offset[1]))
        screen.blit(self.ui_surface, (0, 0))

        self.frame_count_raw += 1 * dt
        self.frame_count = round(self.frame_count_raw)