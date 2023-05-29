'''
Sandbox scene used for mainly testing purposes.
'''

from scripts.constants import SCREEN_DIMENSIONS
from scripts.engine import BoxCamera, Entity, Easings

from scripts.core_systems.talents import get_all_talents
from scripts.core_systems.abilities import get_all_abilities

from scripts.entities.enemy import Stelemental
from scripts.entities.player import Player
from scripts.entities.tiles import Block, Platform, Floor, Ceiling

from scripts.scenes.scene import Scene

from scripts.ui.info_bar import HealthBar
from scripts.ui.card import StandardCard, StatCard
from scripts.ui.text_box import TextBox
from scripts.ui.hotbar import Hotbar

import pygame
import random
import math
import os

class Sandbox(Scene):
    '''
    Variables:
        player: the initialized player class.
        enemy_info: information about how the enemies should spawn.

        camera: the initialized BoxCamera object.
        camera_offset: the value by which the sprite surface should be offset by.

        scene_fx: a dictionary on the different effects the scene will use.

        ui: a collection of ui sprites.
        tiles: a collection of tile sprites.

    Methods:
        on_enemy_spawn(): called with an enemy within the scene spawns.
        on_enemy_death(): called with an enemy within the scene dies.
        
        remove_cards(): the function given to the card object when a card is selected.
        generate_standard_cards(): generates a list of talent/ability cards for the player to choose from.
        generate_stat_cards(): generates a list of stat cards for the player to choose from.
    '''
    
    def __init__(self, scene_handler, surfaces, mouse, sprites=None):
        super().__init__(scene_handler, surfaces, mouse, sprites)

        self.player = Player((2500, 1200), 4)
        self.enemy_info = [[0, 15], [0, 5]]

        self.camera = BoxCamera(self.player)
        self.camera_offset = [0, 0]
        
        self.card_info = {
            'overflow': [],

            'stat_text': None,
            'standard_text': None
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

        self.ui = {
            'healthbar': HealthBar(self.player),
            'temp_guide': [
                TextBox((40, SCREEN_DIMENSIONS[1] - 100), '3: draw cards', size=.5),
                TextBox((40, SCREEN_DIMENSIONS[1] - 50), '0: fullscreen', size=.5)
            ],
            'hotbar': Hotbar(self.player, (SCREEN_DIMENSIONS[0] * .5, SCREEN_DIMENSIONS[1] - 70), 3)
        }

        self.player.healthbar = self.ui['healthbar']
        
        self.tiles = {
            'barrier_y': [
                Floor((0, 1500), (255, 255, 255, 0), (250, 250), 1),
                Ceiling((0, 0), (255, 255, 255, 0), (250, 250), 1)
            ],

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
        
        if event.key == pygame.key.key_code('3'):
            cards = self.generate_stat_cards()
            self.card_info['overflow'].append(self.generate_standard_cards)

            if cards:
                self.in_menu = True
                self.paused = True

                self.scene_fx['entity_dim']['easing'] = 'ease_out_quint'
                self.scene_fx['entity_dim']['type'] = 'in'
                self.scene_fx['entity_dim']['frames'][1] = 30

                for frame in self.ui.values():
                    if isinstance(frame, list):
                        for subframe in frame:
                            subframe.image.set_alpha(100)
                        
                        continue

                    frame.image.set_alpha(100)
                
                self.add_sprites(cards)
                
    def on_enemy_spawn(self):
        ...

    def on_enemy_death(self, enemy):
        ...

    def on_player_death(self):
        ...

    def remove_cards(self, selected_card, cards):
        for card in cards:
            card.tween_info['base_position'] = [card.original_rect.x, card.original_rect.y]
            card.tween_info['position'] = [card.rect.x, 0 - card.rect.height * 1.1]

            if card == selected_card:
                card.tween_info['position'] = [card.rect.x, SCREEN_DIMENSIONS[1] * 1.1]

            card.tween_info['frames'] = 0
            card.tween_info['frames_max'] = 20
                
            card.tween_info['flag'] = 'del'
            card.tween_info['on_finished'] = 'del'

        if self.card_info['overflow']:
            cards = self.card_info['overflow'][0]()

            if cards:
                del self.card_info['overflow'][0]
                self.add_sprites(cards)
                
                return

        self.in_menu = False
        self.paused = False

        self.scene_fx['entity_dim']['type'] = 'out'
        self.scene_fx['entity_dim']['easing'] = 'ease_in_quint'
        self.scene_fx['entity_dim']['frames'][0] = 30
        self.scene_fx['entity_dim']['frames'][1] = 30

        for frame in self.ui.values():
            if isinstance(frame, list):
                for subframe in frame:
                    subframe.image.set_alpha(255)
                
                continue
                    
            frame.image.set_alpha(255)

    def generate_standard_cards(self, count=3):
        def on_select(selected_card, cards):
            if selected_card.draw.DRAW_TYPE == 'TALENT':
                self.player.talents.append(selected_card.draw(self, self.player))
                print(f'selected talent card: {selected_card.draw.DESCRIPTION["name"]}')
                    
            elif selected_card.draw.DRAW_TYPE == 'ABILITY':
                for slot in self.player.abilities.keys():
                    if self.player.abilities[slot] is None:
                        self.player.abilities[slot] = selected_card.draw(self.player)
                        break

                print(f'selected ability card: {selected_card.draw.DESCRIPTION["name"]}')

            self.remove_cards(selected_card, cards)

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
        
        for ability in get_all_abilities():
            if ability.ABILITY_ID in ability_exclude_list:
                continue

            if ability in player_abilities:
                continue

            if not ability.check_draw_condition(self.player):
                continue

            drawables.append(ability)

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
            cards.append(StandardCard((x + (i * 200), y), draw, spawn='y'))

            i += 1

        for card in cards:
            card.cards = cards
            card.on_select = on_select

        return cards

    def generate_stat_cards(self):
        def on_select(selected_card, cards):
            print(f'selected stat card: {selected_card.stat["name"]}')
            
            for i in range(len(selected_card.stat['stat'])):
                self.player.set_stat(selected_card.stat['stat'][i], selected_card.stat['value'][i], True)

            self.remove_cards(selected_card, cards)

        stat_info = [
            {
                'name': 'Vitality', 
                'description': '+ Max Health',
                'stat': ['max_health', 'health'],
                'value': [10, 10]
            },

            {
                'name': 'Potency', 
                'description': '+ Damage',
                'stat': ['base_damage'],
                'value': [5]
            },

            {
                'name': 'Agility', 
                'description': '+ Movespeed',
                'stat': ['max_movespeed'],
                'value': [1]
            },

            {
                'name': 'Dexterity', 
                'description': '+ Critical Strike',
                'stat': ['crit_strike_chance', 'crit_strike_multiplier'],
                'value': [.05, .1]
            },
        ]

        cards = []
        count = len(stat_info)

        x = (SCREEN_DIMENSIONS[0] * .5) - 80
        y = (SCREEN_DIMENSIONS[1] * .5) - 100

        i = None
        if count % 2 == 0:
            i = -(math.floor(count / 2) - .5)
        else:
            i = -math.floor(count / 2)

        for stat in stat_info:
            cards.append(StatCard((x + (i * 200), y), stat, spawn='y'))
            i += 1

        for card in cards:
            card.cards = cards
            card.on_select = on_select

        return cards

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
                if random.randint(1, 3) == 3:
                    self.add_sprites(Stelemental((random.randint(2000, 2500), random.randint(1000, 1600)), 6, True))
                else:
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
