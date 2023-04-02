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

def get_mitigation_dict():
    mitigation_dict = {}

    for dmg_type in DAMAGE_TYPES:
        mitigation_dict[dmg_type] = {}
        mitigation_dict[dmg_type + '&'] = {}

        mitigation_dict['all'] = {}
        mitigation_dict['all&'] = {}

    return mitigation_dict

def register_damage(scene, primary_sprite, secondary_sprite, info):
    if info['type'] not in DAMAGE_TYPES:
        return False
        
    if secondary_sprite.combat_info['immunities']['all']:
        return False

    if secondary_sprite.combat_info['immunities'][info['type'] + '&']:
        return False
        
    if secondary_sprite.combat_info['immunities'][info['type']] > 0:
        return False
        
    info['primary'] = primary_sprite
    info['target'] = secondary_sprite
        
    info['amount'] = random.uniform(
        info['amount'] * (1 - DAMAGE_VARIATION_PERCENTAGE), 
        info['amount'] * (1 + DAMAGE_VARIATION_PERCENTAGE)
        )

    info['amount'] *= primary_sprite.combat_info['damage_multiplier']

    info['crit'] = False
    if primary_sprite.combat_info['crit_strike_chance'] > 0 and round(random.uniform(0, 1), 2) <= primary_sprite.combat_info['crit_strike_chance']:
        info['amount'] *= primary_sprite.combat_info['crit_strike_multiplier']
        info['crit'] = True

    mitigated_amount = 0
    for val in list(secondary_sprite.combat_info['mitigations'][info['type'] + '&'].values()):
        mitigated_amount += val

    for val in list(secondary_sprite.combat_info['mitigations'][info['type']].values()):
        mitigated_amount += val[0]

    for val in list(secondary_sprite.combat_info['mitigations']['all&'].values()):
        mitigated_amount += val

    for val in list(secondary_sprite.combat_info['mitigations']['all'].values()):
        mitigated_amount += val[0]

    if mitigated_amount > 1:
        mitigated_amount = 1

    info['amount'] = info['amount'] * (1 - mitigated_amount)
    info['amount'] = round(info['amount'])

    if secondary_sprite.combat_info['health'] <= info['amount']:
        secondary_sprite.combat_info['health'] = 0
        secondary_sprite.on_death(scene, info)
        
    else:
        secondary_sprite.combat_info['health'] -= info['amount']

    secondary_sprite.on_damaged(scene, info)

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