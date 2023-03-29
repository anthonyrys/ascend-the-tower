from scripts.constants import SCREEN_DIMENSIONS

from scripts.core_systems.talents import Talent, get_all_talents
from scripts.core_systems.abilities import Ability
from scripts.ui.card import Card

import math
import random

MAX_LEVEL = 50

BASE_PLAYER_EXPERIENCE_CAP = 100
PLAYER_EXPERIENCE_CURVE = 2.1

BASE_ENEMY_EXPERIENCE_AMOUNT = 30
ENEMY_EXPERIENCE_CURVE = .95

STATS_PER_POINTS = {
    'speed': [.25, 1],
    'health': 10,
    'damage': 5,
    'crit_strike_chance': .02,
    'crit_strike_multiplier': .05,
}

card_overflow = 0
selecting_cards = False

def level_up(scene):
        player = scene.player

        player.level_info['level'] += 1
        player.level_info['experience'] = 0
        player.level_info['max_experience'] = BASE_PLAYER_EXPERIENCE_CAP + round(math.pow(player.level_info['level'], PLAYER_EXPERIENCE_CURVE))

        generate_cards(scene)

def generate_cards(scene):
    global selecting_cards
    global card_overflow

    if selecting_cards:
        card_overflow += 1
        return
        
    talent_exclude_list = []
    ability_exclude_list = []

    player = scene.player
    player_talents = [t.__class__ for t in player.talents]
    player_abilities = [t.__class__ for t in list(player.abilities.values())]

    drawables = []
    draws = []
    draw_count = 3

    for talent in get_all_talents():
        if talent.TALENT_ID in talent_exclude_list:
            continue

        if talent in player_talents:
            continue

        if not talent.check_draw_condition(player):
            continue

        drawables.append(talent)    

    if len(drawables) < draw_count:
        return
        
    selecting_cards = True
    scene.in_menu = True
    scene.paused = True

    draws = random.sample(drawables, k=draw_count)
    cards = []

    x = (SCREEN_DIMENSIONS[0] * .5) - 80
    y = (SCREEN_DIMENSIONS[1] * .5) - 100
    i = -1

    for draw in draws:
        cards.append(Card((x + (i * 200), y), draw, spawn='y'))
        i += 1

    for card in cards:
        card.drawed_cards = cards
        card.on_select = remove_cards

    scene.add_sprites(cards)

def remove_cards(scene, selected_card, cards):
    global selecting_cards
    global card_overflow

    player = scene.player

    for card in cards:
        card.tween_info['base_position'] = [card.original_rect.x, card.original_rect.y]
        card.tween_info['position'] = [card.rect.x, SCREEN_DIMENSIONS[1]]

        if card == selected_card:
            card.tween_info['position'] = [card.rect.x, 0 - card.rect.height]
            card.tween_info['on_finished'] = lambda: scene.del_sprites(cards)

        card.tween_info['frames'] = 0
        card.tween_info['frames_max'] = 20
            
        card.tween_info['flag'] = 'del'

    player.talents.append(selected_card.draw(player))

    if selected_card.info['type'] == 'talent':
        print(f'selected card: {selected_card.draw.TALENT_ID}')
            
    elif selected_card.info['type'] == 'ability':
        print(f'selected card: {selected_card.draw.ABILITY_ID}')

    scene.in_menu = False
    scene.paused = False
    selecting_cards = False

    if card_overflow > 0:
        generate_cards(scene)
        card_overflow -= 1

def check_experience(scene):
    player = scene.player

    if player.level_info['experience'] < player.level_info['max_experience']:
        return False
    
    amount = abs(player.level_info['experience'] - player.level_info['max_experience'])
    level_up(scene)
    player.on_level_up(scene)
            
    player.level_info['experience'] += amount
    check_experience(scene)
    
    return True

def calculate_experience(level, multiplier=1):
    return round((BASE_ENEMY_EXPERIENCE_AMOUNT + math.pow(level, ENEMY_EXPERIENCE_CURVE)) * multiplier)

def register_experience(scene, amount):
    player = scene.player

    player.level_info['experience'] += amount

    leveled = check_experience(scene)
    player.on_experience_gained(scene)

    return leveled

