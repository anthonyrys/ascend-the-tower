from scripts import SCREEN_DIMENSIONS, PLAYER_COLOR

from scripts.core_systems.talents import get_all_talents
from scripts.core_systems.abilities import get_all_abilities

from scripts.entities.entity import Entity
from scripts.entities.player import Player
from scripts.entities.particle_fx import Circle

from scripts.scenes.scene import Scene

from scripts.services import load_tilemap

from scripts.ui.card import StandardCard, StatCard
from scripts.ui.text_box import TextBox

from scripts.utils import get_sprite_colors
from scripts.utils.camera import BoxCamera
from scripts.utils.easings import Easings

import pygame
import random
import math
import os

class GameScene(Scene):
    def __init__(self, scene_handler, mouse, sprites=None):
        super().__init__(scene_handler, mouse, sprites)

        self.background_surface = pygame.Surface(SCREEN_DIMENSIONS, pygame.SRCALPHA).convert_alpha()
        self.entity_surface = None
        self.ui_surface = pygame.Surface((2000, 2000), pygame.SRCALPHA).convert_alpha()

        self.delay_timers = []

        self.scene_fx = {
            '&dim': {
                'type': None, 
                'amount': 1.0,
                'frames': [0, 0],
                'easing': 'ease_out_quint',
                'threshold': 0
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

        self.player = Player((0, 0), 4)

        self.camera = BoxCamera(self.player)
        self.camera_offset = [0, 0]

        self.ui_elements = []
        self.ui_elements.extend(self.player.get_ui_elements())

        self.card_info = {
            'overflow': [],

            'stat_text': None,
            'standard_text': None,

            'stat_info': [
                {
                    'name': 'Vitality', 
                    'description': '+ Max Health',
                    'stat': ['max_health', 'health'],
                    'value': [20, 20]
                },

                {
                    'name': 'Potency', 
                    'description': '+ Damage',
                    'stat': ['base_damage'],
                    'value': [10]
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
                    'value': [.05, .15]
                },
            ]
        }

        self.load_tilemap()

    def on_scene_end(self):
        self.scene_fx['&dim']['easing'] = 'ease_out_quint'
        self.scene_fx['&dim']['type'] = 'in'
        self.scene_fx['&dim']['amount'] = 1
        self.scene_fx['&dim']['frames'][1] = 30
        self.scene_fx['&dim']['threshold'] = 0

        self.delay_timers.append([90, self.scene_handler.set_new_scene, [self.__class__, {}]])

    def on_enemy_spawn(self):
        ...

    def on_enemy_death(self, enemy):
        ...

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
            cir = Circle(pos, color, random.randint(6, 10), 0)
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

    def load_tilemap(self):
        tilemap = load_tilemap('floor-1')

        self.entity_surface = tilemap['surface']
        self.tiles = tilemap['tiles']
        self.player.rect.x, self.player.rect.y = tilemap['flags']['player_spawn']

    def remove_cards(self, selected_card, cards, flavor_text):
        for card in cards:
            if card == selected_card:
                card.set_position_tween([card.rect.x, SCREEN_DIMENSIONS[1] * 1.1], 20, 'ease_out_quint')

            else:
                card.set_position_tween([card.rect.x, 0 - card.rect.height * 1.1], 20, 'ease_out_quint')

            card.set_flag('del')

            card.on_del_sprite(self, 20)

        flavor_text.set_position_tween((flavor_text.rect.x, 0), 30, 'ease_out_quint')
        flavor_text.set_alpha_tween(0, 25, 'ease_out_sine')

        flavor_text.on_del_sprite(self, 25)

        if self.card_info['overflow']:
            new_cards, new_flavor_text = self.card_info['overflow'][0][0](*self.card_info['overflow'][0][1])

            if new_cards:
                del self.card_info['overflow'][0]

                self.add_sprites(new_cards)
                self.add_sprites(new_flavor_text)
                
                return False

        self.in_menu = False
        self.paused = False

        self.scene_fx['&dim']['type'] = 'out'
        self.scene_fx['&dim']['easing'] = 'ease_in_quint'
        self.scene_fx['&dim']['frames'][0] = 30
        self.scene_fx['&dim']['frames'][1] = 30

        for frame in self.ui_elements:
            frame.image.set_alpha(255)

        return True
    
    def generate_standard_cards(self, count=3):
        def on_select(selected_card, cards, flavor_text):
            if selected_card.draw.DRAW_TYPE == 'TALENT':
                self.player.talents.append(selected_card.draw(self, self.player))
                print(f'selected talent card: {selected_card.draw.DESCRIPTION["name"]}')
                    
            elif selected_card.draw.DRAW_TYPE == 'ABILITY':
                added = False
                for slot in self.player.abilities.keys():
                    if self.player.abilities[slot] is None:
                        self.player.abilities[slot] = selected_card.draw(self.player)
                        added = True
                        break

                if not added:
                    self.card_info['overflow'].insert(0, [self.generate_ability_fail_cards, [selected_card]])

                print(f'selected ability card: {selected_card.draw.DESCRIPTION["name"]}')

            self.remove_cards(selected_card, cards, flavor_text)

        if count <= 0:
            return None, None
        
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
            return None, None
        
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

        flavor_text = TextBox((0, 0), 'the towers knowledge reveals itself..', color=(255, 255, 255))

        flavor_text.rect.x = ((SCREEN_DIMENSIONS[0] * .5) - (flavor_text.image.get_width() * .5))
        flavor_text.image.set_alpha(0)

        flavor_text.set_position_tween(((SCREEN_DIMENSIONS[0] * .5) - (flavor_text.image.get_width() * .5), y - 150), 45, 'ease_out_quint')
        flavor_text.set_alpha_tween(255, 45, 'ease_out_sine')

        for card in cards:
            card.cards = cards
            card.flavor_text = flavor_text
            card.on_select = on_select

        return cards, flavor_text

    def generate_ability_fail_cards(self, previous_selected_card):
        def on_select(selected_card, cards, flavor_text):
            for inp in self.player.abilities.keys():
                if self.player.abilities[inp].__class__ != selected_card.draw:
                    continue
                
                self.player.abilities[inp].end()
                self.player.abilities[inp] = previous_selected_card.draw(self.player)
                
                break

            print(f'replaced ability card: {selected_card.draw.DESCRIPTION["name"]} -> {previous_selected_card.draw.DESCRIPTION["name"]}')

            self.remove_cards(selected_card, cards, flavor_text)

        existing_abilities = [a for a in self.player.abilities.values() if a.ABILITY_ID[0] != '@']
        draw_count = len(existing_abilities)

        x = (SCREEN_DIMENSIONS[0] * .5) - 80
        y = (SCREEN_DIMENSIONS[1] * .5) - 100

        cards = []

        i = None
        if draw_count % 2 == 0:
            i = -(math.floor(draw_count / 2) - .5)
        else:
            i = -math.floor(draw_count / 2)

        for draw in existing_abilities:
            cards.append(StandardCard((x + (i * 200), y), draw.__class__, spawn='y'))

            i += 1

        flavor_text = TextBox((0, 0), 'choose an ability to discard..', color=(255, 255, 255))

        flavor_text.rect.x = ((SCREEN_DIMENSIONS[0] * .5) - (flavor_text.image.get_width() * .5))
        flavor_text.image.set_alpha(0)

        flavor_text.set_position_tween(((SCREEN_DIMENSIONS[0] * .5) - (flavor_text.image.get_width() * .5), y - 150), 45, 'ease_out_quint')
        flavor_text.set_alpha_tween(255, 45, 'ease_out_sine')

        for card in cards:
            card.cards = cards
            card.flavor_text = flavor_text
            card.on_select = on_select

        return cards, flavor_text

    def generate_stat_cards(self):
        def on_select(selected_card, cards, flavor_text):
            print(f'selected stat card: {selected_card.stat["name"]}')
            
            for i in range(len(selected_card.stat['stat'])):
                self.player.set_stat(selected_card.stat['stat'][i], selected_card.stat['value'][i], True)

            self.remove_cards(selected_card, cards, flavor_text)

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

        flavor_text = TextBox((0, 0), 'you feel yourself become stronger..', color=(255, 255, 255))

        flavor_text.rect.x = ((SCREEN_DIMENSIONS[0] * .5) - (flavor_text.image.get_width() * .5))
        flavor_text.image.set_alpha(0)

        flavor_text.set_position_tween(((SCREEN_DIMENSIONS[0] * .5) - (flavor_text.image.get_width() * .5), y - 150), 45, 'ease_out_quint')
        flavor_text.set_alpha_tween(255, 45, 'ease_out_sine')

        for card in cards:
            card.cards = cards
            card.flavor_text = flavor_text
            card.on_select = on_select

        return cards, flavor_text

    def apply_scene_fx(self, dt):
        entity_display = pygame.Surface(SCREEN_DIMENSIONS).convert_alpha()
        entity_display.fill((0, 0, 0, 0))

        entity_display.blit(self.entity_surface, (-self.camera_offset[0], -self.camera_offset[1]))

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

        self.background_surface.fill((0, 0, 0, 255), entity_view)
        self.entity_surface.fill((0, 0, 0, 0), entity_view)
        self.ui_surface.fill((0, 0, 0, 0), self.view)

        display_order = self.sort_sprites(self.sprite_list)
        for _, v in sorted(display_order.items()):
            for sprite in v: 
                if not sprite.active:
                    continue

                if isinstance(sprite, Entity):
                    sprite.display(self, entity_dt)
                    continue

                sprite.display(self, dt)

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

        display_list = self.apply_scene_fx(dt)
        screen.blit(self.background_surface, (0, 0))
        if display_list[3] and self.scene_fx['&dim']['threshold'] == 2:
            screen.blit(display_list[3], (0, 0))

        screen.blit(display_list[1], (display_list[1].get_rect(center=screen.get_rect().center)))
        if display_list[3] and self.scene_fx['&dim']['threshold'] == 1:
            screen.blit(display_list[3], (0, 0))
            
        screen.blit(self.ui_surface, (0, 0))
        if display_list[3] and self.scene_fx['&dim']['threshold'] == 0:
            screen.blit(display_list[3], (0, 0))
    
        self.mouse.display(self, screen)

        self.frame_count_raw += 1 * dt
        self.frame_count = round(self.frame_count_raw)

        super().display(screen, clock, dt)
    