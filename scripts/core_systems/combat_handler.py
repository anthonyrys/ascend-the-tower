import random

DAMAGE_TYPES = ['contact', 'physical', 'magical', 'special']
HEAL_TYPES = ['passive', 'status', 'special']

DAMAGE_VARIATION_PERCENTAGE = .1

def get_immunity_dict():
    immunity_list = {}

    for dmg_type in DAMAGE_TYPES:
        immunity_list[dmg_type] = 0
        immunity_list[dmg_type + '&'] = False
        immunity_list['all'] = False

    return immunity_list

def register_damage(scene, primary_sprite, secondary_sprite, info):
    if info['type'] not in DAMAGE_TYPES:
        return False
        
    if secondary_sprite.combat_info['immunities']['all']:
        return False

    if secondary_sprite.combat_info['immunities'][info['type'] + '&']:
        return False
        
    if secondary_sprite.combat_info['immunities'][info['type']] > 0:
        return False
        
    info['target'] = secondary_sprite
        
    info['amount'] = random.uniform(
        info['amount'] * (1 - DAMAGE_VARIATION_PERCENTAGE), 
        info['amount'] * (1 + DAMAGE_VARIATION_PERCENTAGE)
        )

    info['crit'] = False
    if primary_sprite.combat_info['crit_strike_chance'] > 0 and round(random.uniform(0, 1), 2) <= primary_sprite.combat_info['crit_strike_chance']:
        info['amount'] *= primary_sprite.combat_info['crit_strike_multiplier']
        info['crit'] = True

    info['amount'] = round(info['amount'])
    if secondary_sprite.combat_info['health'] <= info['amount']:
        secondary_sprite.combat_info['health'] = 0
        secondary_sprite.on_death(scene, info)
        
    else:
        secondary_sprite.combat_info['health'] -= info['amount']

    secondary_sprite.on_damaged(scene, primary_sprite, info)

    # print(f'{primary_sprite} damage >> {secondary_sprite}; ({info["type"]}, {info["amount"]}, {info["crit"]})')
    return info

def register_heal(scene, primary_sprite, info):
    if info['type'] not in HEAL_TYPES:
        return
        
    info['amount'] = round(info['amount'])
    primary_sprite.combat_info['health'] += info['amount']

    if primary_sprite.combat_info['health'] > primary_sprite.combat_info['max_health']:
        primary_sprite.combat_info['health'] = primary_sprite.combat_info['max_health']

    primary_sprite.on_healed(scene, info)