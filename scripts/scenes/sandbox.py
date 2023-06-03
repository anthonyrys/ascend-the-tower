'''
Holds the Sandbox class.
'''

from scripts.constants import SCREEN_DIMENSIONS, PLAYER_COLOR
from scripts.engine import BoxCamera, Entity, Easings, get_sprite_colors

from scripts.core_systems.talents import get_all_talents
from scripts.core_systems.abilities import get_all_abilities
from scripts.core_systems.wave_handler import WaveHandler

from scripts.entities.player import Player
from scripts.entities.particle_fx import Circle
from scripts.entities.tiles import Barrier, Floor, Ceiling

from scripts.scenes.scene import Scene

from scripts.ui.card import StandardCard, StatCard
from scripts.ui.text_box import TextBox

import pygame
import random
import math
import os

class Sandbox(Scene):
    '''
    Variables:
        delay_timers: list of functions to be called after a certain amount of time.

        scene_fx: special effects for the scene surfaces.
        
        tiles: a collection of tile sprites.

        player: the initialized player class.

        camera: the initialized BoxCamera object.
        camera_offset: the value by which the sprite surface should be offset by.

        ui_elements: a collection of ui sprites.

        wave_handler: the initialized WaveHandler object.

        card_info: information on how the card ui should function.

    Methods:
        on_scene_end(): called when the scene ends; calls SceneHandler set_new_scene().

        on_enemy_spawn(): called once an enemy within the scene spawns.
        on_enemy_death(): called once an enemy within the scene dies.
        
        on_player_death(): called once the player dies; begins the game over process.

        remove_cards(): the function given to the card object when a card is selected.
        generate_standard_cards(): generates a list of talent/ability cards for the player to choose from.
        generate_stat_cards(): generates a list of stat cards for the player to choose from.

        apply_scene_fx: applies effects for the scene surfaces according to the scene_fx dictionary,
    '''

    def __init__(self, scene_handler, surfaces, mouse, sprites=None):
        super().__init__(scene_handler, surfaces, mouse, sprites)
        
        self.delay_timers = []

        self.scene_fx = {
            '&dim': {
                'type': None, 
                'amount': 1.0,
                'frames': [0, 0],
                'easing': 'ease_out_quint'
            },

            'entity_dim': {
                'type': None, 
                'amount': 0.0,
                'frames': [0, 0],
                'easing': 'ease_out_quint'
            },

            'entity_zoom': {
                'type': None, 
                'amount': 0.0,
                'frames': [0, 0],
                'easing': 'ease_out_quint'
            }
        }

        self.scene_fx['&dim']['type'] = 'out'
        self.scene_fx['&dim']['easing'] = 'ease_out_cubic'
        self.scene_fx['&dim']['frames'][0] = 45
        self.scene_fx['&dim']['frames'][1] = 45

        self.tiles = {
            'barrier_y': [
                Floor((0, 1500), (255, 255, 255, 0), (250, 250), 1),
                Ceiling((0, 0), (255, 255, 255, 0), (250, 250), 1)
            ],

            'barrier_x': [
                Barrier((250, 0), (255, 255, 255, 0), (250, 250), ['player'], 1),        
                Barrier((4500, 0), (255, 255, 255, 0), (250, 250), ['player'], 1)
            ],

            'floor': [
                Floor((0, 1500), (255, 255, 255), (5000, 25), 1)
            ],
        }

        self.player = Player((self.tiles['floor'][0].center_position[0], 1200), 4)

        self.camera = BoxCamera(self.player)
        self.camera_offset = [0, 0]

        self.ui_elements = []
        self.ui_elements.extend(self.player.get_ui_elements())
        self.ui_elements.append(TextBox((40, SCREEN_DIMENSIONS[1] - 50), '0: fullscreen', size=.5))
        self.ui_elements.append(TextBox((40, SCREEN_DIMENSIONS[1] - 100), '3: draw cards', size=.5))
        self.ui_elements.append(TextBox((40, SCREEN_DIMENSIONS[1] - 150), '4: spawn enemy', size=.5))

        self.wave_handler = WaveHandler(self)

        self.card_info = {
            'overflow': [],

            'stat_text': None,
            'standard_text': None,

            'stat_info': [
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
        }

        self.add_sprites(self.player)

        for sprite_list in self.tiles.values():
            for sprite in sprite_list:
                self.add_sprites(sprite)

        self.add_sprites(self.ui_elements)

    def on_scene_end(self):
        self.scene_fx['&dim']['easing'] = 'ease_out_quint'
        self.scene_fx['&dim']['type'] = 'in'
        self.scene_fx['&dim']['amount'] = 1
        self.scene_fx['&dim']['frames'][1] = 30

        self.delay_timers.append([90, self.scene_handler.set_new_scene, [self.__class__, {}]])

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

                self.scene_fx['entity_dim']['amount'] = .75
                self.scene_fx['entity_dim']['frames'][1] = 30

                for frame in self.ui_elements:
                    frame.image.set_alpha(100)
                
                self.add_sprites(cards)

        elif event.key == pygame.key.key_code('4'):
            enemy = random.choice(self.wave_handler.ENEMY_INFO[1])(self.wave_handler.get_spawn_position(), 6)

            self.add_sprites(enemy)

    def on_enemy_spawn(self):
        self.wave_handler.on_enemy_spawn()

    def on_enemy_death(self, enemy):
        self.wave_handler.on_enemy_death()

    def on_player_death(self):
        self.player.overrides['death'] = True

        self.scene_fx['entity_zoom']['easing'] = 'ease_in_quint'
        self.scene_fx['entity_zoom']['type'] = 'out'
        self.scene_fx['entity_zoom']['frames'][0] = 45
        self.scene_fx['entity_zoom']['frames'][1] = 45

        self.camera.set_camera_shake(60, 12)

        pos = self.player.center_position
        particles = []

        for color in get_sprite_colors(self.player, 2):
            cir = Circle(pos, color, 10, 0)
            cir.set_goal(
                        150, 
                        position=(pos[0] + random.randint(-450, 450), pos[1] + random.randint(-350, -250)), 
                        radius=0, 
                        width=0
                    )
            cir.set_gravity(5)
            cir.set_easings(radius='ease_out_sine')

            particles.append(cir)

        for _ in range(7):
            cir = Circle(pos, PLAYER_COLOR, 9, 0)
            cir.set_goal(
                        150, 
                        position=(pos[0] + random.randint(-250, 250), pos[1] + random.randint(-250, 250)), 
                        radius=0, 
                        width=0
                    )

            cir.glow['active'] = True
            cir.glow['size'] = 1.6
            cir.glow['intensity'] = .25

            particles.append(cir)
        
        self.add_sprites(particles)
        self.delay_timers.append([90, self.on_scene_end, []])

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

        for frame in self.ui_elements:
            frame.image.set_alpha(255)

        self.player.combat_info['health'] = self.player.combat_info['max_health']
        
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

        cards = []
        count = len(self.card_info['stat_info'])

        x = (SCREEN_DIMENSIONS[0] * .5) - 80
        y = (SCREEN_DIMENSIONS[1] * .5) - 100

        i = None
        if count % 2 == 0:
            i = -(math.floor(count / 2) - .5)
        else:
            i = -math.floor(count / 2)

        for stat in self.card_info['stat_info']:
            cards.append(StatCard((x + (i * 200), y), stat, spawn='y'))
            i += 1

        for card in cards:
            card.cards = cards
            card.on_select = on_select

        return cards

    def apply_scene_fx(self):
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

        if self.scene_fx['entity_zoom']['type']:
            abs_prog = self.scene_fx['entity_zoom']['frames'][0] / self.scene_fx['entity_zoom']['frames'][1]
            zoom = 1.0
            
            if self.scene_fx['entity_zoom']['type'] == 'in':
                zoom += self.scene_fx['entity_zoom']['amount'] * getattr(Easings, self.scene_fx['entity_zoom']['easing'])(abs_prog)
                if self.scene_fx['entity_zoom']['frames'][0] < self.scene_fx['entity_zoom']['frames'][1]:
                    self.scene_fx['entity_zoom']['frames'][0] += 1

            elif self.scene_fx['entity_zoom']['type'] == 'out':
                zoom += self.scene_fx['entity_zoom']['amount'] * getattr(Easings, self.scene_fx['entity_zoom']['easing'])(abs_prog)
                if self.scene_fx['entity_zoom']['frames'][0] > 0:
                    self.scene_fx['entity_zoom']['frames'][0] -= 1
                else:
                    self.scene_fx['entity_zoom']['type'] = None

            entity_display = pygame.transform.scale(entity_display, (entity_display.get_width() * zoom, entity_display.get_height() * zoom)).convert_alpha()

        dim_display = None

        if self.scene_fx['&dim']['type']:
            abs_prog = self.scene_fx['&dim']['frames'][0] / self.scene_fx['&dim']['frames'][1]
            dim_display = pygame.Surface(SCREEN_DIMENSIONS)
            dim_display.fill((0, 0, 0))

            if self.scene_fx['&dim']['type'] == 'in':
                dim_display.set_alpha(255 * (self.scene_fx['&dim']['amount'] * getattr(Easings, self.scene_fx['&dim']['easing'])(abs_prog)))
                if self.scene_fx['&dim']['frames'][0] < self.scene_fx['&dim']['frames'][1]:
                    self.scene_fx['&dim']['frames'][0] += 1

            elif self.scene_fx['&dim']['type'] == 'out':
                dim_display.set_alpha(255 * (self.scene_fx['&dim']['amount'] * getattr(Easings, self.scene_fx['&dim']['easing'])(abs_prog)))
                if self.scene_fx['&dim']['frames'][0] > 0:
                    self.scene_fx['&dim']['frames'][0] -= 1
                else:
                    self.scene_fx['&dim']['type'] = None

        return [None, entity_display, None, dim_display]

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

        remove_list = []
        for i in range(len(self.delay_timers)):
            if self.delay_timers[i][0] > 0:
                self.delay_timers[i][0] -= 1

                if self.delay_timers[i][0] <= 0 and self.delay_timers[i][1]:
                    self.delay_timers[i][1](*self.delay_timers[i][2])
                    remove_list.append(self.delay_timers[i])

        for element in remove_list:
            self.delay_timers.remove(element)

        self.camera_offset = self.camera.update(dt)
        
        display_list = self.apply_scene_fx()
        screen.blit(self.background_surface, (0, 0))
        screen.blit(display_list[1], (display_list[1].get_rect(center=screen.get_rect().center)))
        screen.blit(self.ui_surface, (0, 0))

        if display_list[3]:
            screen.blit(display_list[3], (0, 0))

        self.mouse.display(self, screen)

        self.frame_count_raw += 1 * dt
        self.frame_count = round(self.frame_count_raw)
