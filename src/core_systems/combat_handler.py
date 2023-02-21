import pygame

class CombatMethods:
    DAMAGE_TYPES = ['contact', 'physical', 'magical', 'special']
    HEAL_TYPES = ['potion', 'status', 'special']

    @staticmethod
    def register_damage(scene, primary_sprite, secondary_sprite, info):
        if info['type'] not in CombatMethods.DAMAGE_TYPES:
            return False

        if secondary_sprite.immunities.get(info['type'] + '&'):
            return False
        
        if secondary_sprite.immunities.get(info['type']):
            if secondary_sprite.immunities[info['type']] > 0:
                return False
        
        if secondary_sprite.combat_info['health'] < info['amount']:
            secondary_sprite.combat_info['health'] = 0
        
        else:
            secondary_sprite.combat_info['health'] -= info['amount']

        secondary_sprite.on_damaged(scene, primary_sprite, info)

        return True

    @staticmethod
    def register_heal(scene, primary_sprite, info):
        if info['type'] not in CombatMethods.HEAL_TYPES:
            return
        
        primary_sprite.combat_info['health'] += info['amount']

        if primary_sprite.combat_info['health'] > primary_sprite.combat_info['max_health']:
            primary_sprite.combat_info['health'] = primary_sprite.combat_info['max_health']

        primary_sprite.on_healed(scene, info)