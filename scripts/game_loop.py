from scripts import SCREEN_DIMENSIONS, PLAYER_COLOR, ENEMY_COLOR

from scripts.core_systems.talents import get_all_talents
from scripts.core_systems.abilities import get_all_abilities

from scripts.entities.enemy import ENEMIES
from scripts.entities.entity import Entity
from scripts.entities.tiles import Tile
from scripts.entities.player import Player
from scripts.visual_fx.particle import Circle
from scripts.entities.interactables import StandardCardInteractable

from scripts.scene import Scene

from scripts.tilemap_loader import load_tilemap

from scripts.ui.card import StandardCard, StatCard
from scripts.ui.text_box import TextBox

from scripts.tools import get_sprite_colors, get_distance
from scripts.camera import BoxCamera
from scripts.tools.bezier import presets, get_bezier_point

import pygame
import random
import math

class GameLoop(Scene):
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
                'bezier': presets['ease_out'],
                'threshold': 0
            },

            'entity_zoom': {
                'type': None, 
                'amount': 0.0,
                'frames': [0, 0],
                'bezier': presets['ease_out']
            }
        }

        self.player = Player((0, 0), 5)
        self.tiles = None

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

        self.enemy_info = {
            'enemies': [0, 3],

            'card_death_counter': 0,

            'spawn_cooldown': [105, 105],
            'spawn_positions': {},
            'spawn_distance': 750
        }

        self.player_info = {
            'last_ground_position': [0, 0]
        }

        self.ui_elements.extend([
            TextBox((10, 130), '3: draw regular cards', size=.5),
            TextBox((10, 160), '4: draw stat cards', size=.5),
            TextBox((10, 190), '0: fullscreen', size=.5)
        ])

        self.add_sprites(self.ui_elements)
        self.add_sprites(self.player)
    
        self.load_tilemap()
        self.load_intro()

    def on_key_down(self, event):
        super().on_key_down(event)
        
        if self.paused:
            return
        
        if event.key == pygame.K_3:
            cards, text = self.generate_standard_cards()
            if cards and text:
                self.load_card_event(cards, text)

        elif event.key == pygame.K_4:
            cards, text = self.generate_stat_cards()
            if cards and text:
                self.load_card_event(cards, text)

    def on_scene_end(self):
        self.scene_fx['&dim']['bezier'] = presets['ease_out']
        self.scene_fx['&dim']['type'] = 'in'
        self.scene_fx['&dim']['amount'] = 1
        self.scene_fx['&dim']['frames'][1] = 30
        self.scene_fx['&dim']['threshold'] = 0

        self.delay_timers.append([90, self.scene_handler.set_new_scene, [self.__class__, {}]])

    def on_enemy_spawn(self):
        self.enemy_info['enemies'][0] += 1

    def on_enemy_death(self, enemy):
        self.enemy_info['card_death_counter'] += 1
        self.enemy_info['enemies'][0] -= 1

        spawn_card = round(math.pow(self.enemy_info['card_death_counter'], 2.86))
        if spawn_card < random.randint(1, 100):
            return
        
        self.enemy_info['card_death_counter'] = 0

        position = [
            enemy.center_position[0],
            enemy.center_position[1] - random.randint(25, 50)
        ]

        card = StandardCardInteractable(enemy.center_position, None, None, 9, 0)

        collide_tiles = True
        while collide_tiles:
            collide_tiles = []
            for tile in self.get_sprites('tile'):
                if tile.rect.collidepoint(position):
                    position[1] -= tile.rect.height * 2
                    collide_tiles.append(tile)

        card.set_x_bezier(position[0] + random.randint(-100, 100) * 2, 75, [[0, 0], [.5, 1.5], [1, 0], [1, 0], 0])
        card.set_y_bezier(position[1], 75, [[0, 0], [2.65, 0.6], [1.1, 0.45], [1, 0], 0])
        card.set_alpha_bezier(255, 30, [*presets['rest'], 0])

        self.add_sprites(card)

    def on_player_death(self):
        self.delay_timers.append([90, self.on_scene_end, []])

        self.player.overrides['death'] = True

        self.scene_fx['entity_zoom']['bezier'] = presets['ease_in']
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
            cir.set_beziers(radius=presets['ease_out'])

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
        
        for frame in self.ui_elements:
            frame.set_alpha_bezier(0, 30, presets['ease_out'])

        self.add_sprites(particles)

    def on_floor_clear(self):
        self.player.overrides['inactive-all'] = True
        self.player.velocity = [0, 0]

        particles = []
        pos = self.player.center_position
        for _ in range(6):
            cir = Circle(pos, PLAYER_COLOR, random.randint(5, 7), 0)
            cir.set_goal(
                        75, 
                        position=(pos[0] + random.randint(-75, 75), pos[1] + random.randint(-75, 75)), 
                        radius=0, 
                        width=0
                    )
            
            cir.glow['active'] = True

            particles.append(cir)

        player_particle = Circle(pos, PLAYER_COLOR, 8, 0)
        player_particle.set_goal(90, position=[pos[0], pos[1] - 500], radius=8, width=0)
        player_particle.set_beziers(position=[[0, 0], [-.25, 1], [0, 1], [1, 0], 0])

        player_particle.glow['active'] = True
        player_particle.glow['size'] = 1.5
        player_particle.glow['intensity'] = .4

        self.add_sprites(particles)
        self.add_sprites(player_particle)

        self.scene_fx['&dim']['type'] = 'in'
        self.scene_fx['&dim']['amount'] = 1
        self.scene_fx['&dim']['threshold'] = 0
        self.scene_fx['&dim']['bezier'] = presets['ease_in']
        self.scene_fx['&dim']['frames'][0] = 0
        self.scene_fx['&dim']['frames'][1] = 75

        for frame in self.ui_elements:
            frame.set_alpha_bezier(0, 75, presets['ease_in'])

        self.delay_timers.append([120, self.load_tilemap, []])
        self.delay_timers.append([120, self.load_intro, []])

    def register_enemy_flags(self, dt):
        if not self.enemy_info['spawn_positions'] or self.enemy_info['enemies'][0] >= self.enemy_info['enemies'][1]:
            return

        if self.enemy_info['spawn_cooldown'][0] > 0:
            self.enemy_info['spawn_cooldown'][0] -= 1 * dt
                        
        if self.enemy_info['spawn_cooldown'][0] > 0:
            return

        elgible_spawns = {}
        for spawn_type, pos_list in self.enemy_info['spawn_positions'].items():
            for position in pos_list:
                if get_distance(self.player.center_position, position) > self.enemy_info['spawn_distance']:
                    continue
                
                if spawn_type not in elgible_spawns:
                    elgible_spawns[spawn_type] = []

                elgible_spawns[spawn_type].append(position)

        if not elgible_spawns:
            return
        
        positions = []
        for i, v in elgible_spawns.items():
            for p in v:
                positions.append([i, p, get_distance(self.player.center_position, p)])

        min_value = min([p[2] for p in positions])
        
        for position in positions:
            if position[2] != min_value:
                continue

            self.enemy_info['spawn_cooldown'][0] = self.enemy_info['spawn_cooldown'][1]

            enemy_position = [position[1][0] + random.randint(-50, 50), position[1][1] + random.randint(-50, 50)]
            enemy = ENEMIES[1][position[0] - 1](enemy_position, 6)

            particle_position = [enemy_position[0] + enemy.image.get_width() * .5, enemy_position[1] + enemy.image.get_height() * .5]
            particle = Circle(particle_position, ENEMY_COLOR, 60, 2)
            particle.set_goal(30, radius=0, width=1, alpha=0)

            particles = []
            for _ in range(6):
                cir = Circle(particle_position, ENEMY_COLOR, random.randint(8, 10), 0)
                cir.set_goal(
                            75, 
                            position=(particle_position[0] + random.randint(-75, 75), particle_position[1] + random.randint(-75, 75)), 
                            radius=0, 
                            width=0
                        )

                particles.append(cir)

            self.add_sprites(particle)

            self.on_enemy_spawn()
            self.delay_timers.append([30, self.add_sprites, [enemy], 1])
            self.delay_timers.append([30, self.add_sprites, [particles], 1])

    def register_player_flags(self):
        if not self.entity_surface:
            return
        
        if self.player.collide_points['bottom']:
            self.player_info['last_ground_position'] = self.player.true_position

        if self.player.rect.y >= self.entity_surface.get_height() - 250:
            self.player.rect.x = self.player_info['last_ground_position'][0]
            self.player.rect.y = self.player_info['last_ground_position'][1] - 25

            self.player.velocity = [0, 0]
            self.camera.box.center = self.player.true_position
            self.camera.set_camera_tween(30)

    def load_tilemap(self):
        if self.tiles:
            self.del_sprites(self.tiles)

        tilemap = load_tilemap('floor-1')

        self.entity_surface = tilemap['surface']
        self.tiles = tilemap['tiles']
        self.flags = tilemap['flags']

        self.player.overrides['inactive-all'] = True
        self.player.rect.x, self.player.rect.y = tilemap['flags']['player_spawn'][0]
        for flag in tilemap['flags']:
            if not flag.split('_'):
                continue

            if flag.split('_')[0] + flag.split('_')[1] == 'enemyspawn':
                self.enemy_info['spawn_positions'][int(flag.split('_')[2])] = tilemap['flags'][flag]

        self.add_sprites(self.tiles)

    def load_intro(self):
        particles = []
        pos = self.player.center_position
        for _ in range(6):
            cir = Circle(pos, PLAYER_COLOR, random.randint(5, 7), 0)
            cir.set_goal(
                        75, 
                        position=(pos[0] + random.randint(-75, 75), pos[1] + random.randint(-75, 75)), 
                        radius=0, 
                        width=0
                    )
            
            cir.glow['active'] = True

            particles.append(cir)

        player_particle = Circle([pos[0], pos[1] + 300], PLAYER_COLOR, 8, 0)
        player_particle.set_goal(60, position=pos, radius=8, width=0)
        player_particle.set_beziers(position=[[0, 0], [1.25, .25], [1.25, 0], [1, 0], 0])
        player_particle.glow['active'] = True
        player_particle.glow['size'] = 1.5
        player_particle.glow['intensity'] = .4

        floor_text = TextBox((0, 0), 'Floor 1')
        floor_text.rect.x = (SCREEN_DIMENSIONS[0] / 2) - (floor_text.image.get_width() / 2)
        floor_text.rect.y = 100

        self.delay_timers.append([10, self.add_sprites, [player_particle]])
        self.delay_timers.append([70, self.add_sprites, [particles]])

        self.delay_timers.append([90, floor_text.set_alpha_bezier, [0, 45, presets['ease_out']]])
        self.delay_timers.append([90, floor_text.set_y_bezier, [50, 45, presets['ease_out']]])

        self.delay_timers.append([70, self.player.set_override, ['inactive-all', False]])

        for frame in self.ui_elements:
            self.delay_timers.append([90, frame.set_alpha_bezier, [255, 60, presets['ease_out']]]) 

        self.scene_fx['&dim']['type'] = 'out'
        self.scene_fx['&dim']['bezier'] = presets['ease_out']
        self.scene_fx['&dim']['frames'][0] = 60
        self.scene_fx['&dim']['frames'][1] = 60

        self.camera.box.center = pos
        self.add_sprites(floor_text)

    def load_card_event(self, cards, flavor_text):    
        self.in_menu = True
        self.paused = True

        self.scene_fx['&dim']['bezier'] = presets['ease_out']
        self.scene_fx['&dim']['type'] = 'in'

        self.scene_fx['&dim']['amount'] = .75
        self.scene_fx['&dim']['frames'][1] = 30
            
        self.scene_fx['&dim']['threshold'] = 1

        for frame in self.ui_elements:
            frame.set_alpha_bezier(0, 30, presets['ease_out'])

        self.add_sprites(cards)
        self.add_sprites(flavor_text)

    def remove_cards(self, selected_card, cards, flavor_text):
        for card in cards:
            if card == selected_card:
                card.set_y_bezier(SCREEN_DIMENSIONS[1] * 1.1, 20, presets['ease_out'])
            else:
                card.set_y_bezier(0 - card.rect.height * 1.1, 20, presets['ease_out'])

            card.set_flag('del')

            card.on_del_sprite(self, 20)

        flavor_text.set_y_bezier(0, 30, presets['ease_out'])
        flavor_text.set_alpha_bezier(0, 25, [*presets['rest'], 0])

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
        self.scene_fx['&dim']['bezier'] = presets['ease_in']
        self.scene_fx['&dim']['frames'][0] = 30
        self.scene_fx['&dim']['frames'][1] = 30

        for frame in self.ui_elements:
            frame.set_alpha_bezier(255, 30, presets['ease_out'])

        return True
    
    def generate_standard_cards(self, count=3):
        def on_select(selected_card, cards, flavor_text):
            if selected_card.draw.DRAW_TYPE == 'TALENT':
                self.player.talents.append(selected_card.draw(self, self.player))
                # print(f'selected talent card: {selected_card.draw.DESCRIPTION["name"]}')
                    
            elif selected_card.draw.DRAW_TYPE == 'ABILITY':
                added = False
                for slot in self.player.abilities.keys():
                    if self.player.abilities[slot] is None:
                        self.player.abilities[slot] = selected_card.draw(self.player)
                        added = True
                        break

                if not added:
                    self.card_info['overflow'].insert(0, [self.generate_ability_fail_cards, [selected_card]])

                # print(f'selected ability card: {selected_card.draw.DESCRIPTION["name"]}')

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

        flavor_text.set_y_bezier(y - 150, 30, presets['ease_out'])
        flavor_text.set_alpha_bezier(255, 45, [*presets['rest'], 0])

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

            # print(f'replaced ability card: {selected_card.draw.DESCRIPTION["name"]} -> {previous_selected_card.draw.DESCRIPTION["name"]}')

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

        flavor_text.set_y_bezier(y - 150, 30, presets['ease_out'])
        flavor_text.set_alpha_bezier(255, 45, [*presets['rest'], 0])

        for card in cards:
            card.cards = cards
            card.flavor_text = flavor_text
            card.on_select = on_select

        return cards, flavor_text

    def generate_stat_cards(self):
        def on_select(selected_card, cards, flavor_text):
            # print(f'selected stat card: {selected_card.stat["name"]}')
            
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

        flavor_text = TextBox((0, 0), 'you feel yourself become stronger..', color=PLAYER_COLOR)

        flavor_text.rect.x = ((SCREEN_DIMENSIONS[0] * .5) - (flavor_text.image.get_width() * .5))
        flavor_text.image.set_alpha(0)

        flavor_text.set_y_bezier(y - 150, 30, presets['ease_out'])
        flavor_text.set_alpha_bezier(255, 45, [*presets['rest'], 0])

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
                zoom += self.scene_fx['entity_zoom']['amount'] * get_bezier_point(abs_prog, *self.scene_fx['entity_zoom']['bezier'])
                if self.scene_fx['entity_zoom']['frames'][0] < self.scene_fx['entity_zoom']['frames'][1]:
                    self.scene_fx['entity_zoom']['frames'][0] += 1

            elif self.scene_fx['entity_zoom']['type'] == 'out':
                zoom += self.scene_fx['entity_zoom']['amount'] * get_bezier_point(abs_prog, *self.scene_fx['entity_zoom']['bezier'])
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
                dim_display.set_alpha(255 * (self.scene_fx['&dim']['amount'] * get_bezier_point(abs_prog, *self.scene_fx['&dim']['bezier'])))
                if self.scene_fx['&dim']['frames'][0] < self.scene_fx['&dim']['frames'][1]:
                    self.scene_fx['&dim']['frames'][0] += 1

            elif self.scene_fx['&dim']['type'] == 'out':
                dim_display.set_alpha(255 * (self.scene_fx['&dim']['amount'] * get_bezier_point(abs_prog, *self.scene_fx['&dim']['bezier'])))
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
            self.camera_offset[0] - self.view.width * .25, self.camera_offset[1] - self.view.height * .25, 
            self.view.width * 1.5, self.view.height * 1.5
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
                    if isinstance(sprite, Tile):
                        if not entity_view.colliderect(sprite.rect):
                            continue

                    sprite.display(self, entity_dt)
                    continue

                sprite.display(self, dt)

        remove_list = []
        for i in range(len(self.delay_timers)):
            if self.delay_timers[i][0] > 0:
                if len(self.delay_timers[i]) == 4:
                    if self.delay_timers[i][3] == 1:
                        self.delay_timers[i][0] -= 1 * entity_dt
                else:
                    self.delay_timers[i][0] -= 1

                if self.delay_timers[i][0] <= 0 and self.delay_timers[i][1]:
                    self.delay_timers[i][1](*self.delay_timers[i][2])
                    remove_list.append(self.delay_timers[i])

        for element in remove_list:
            self.delay_timers.remove(element)

        self.register_enemy_flags(entity_dt)
        self.register_player_flags()

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
    