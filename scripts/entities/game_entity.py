'''
Holds the game entity class.
'''

from scripts.engine import Entity

from scripts.core_systems.combat_handler import get_immunity_dict, get_mitigation_dict, register_heal

import pygame

class GameEntity(Entity):
    '''
    Inherited from entity class.
    Holds variables and methods that the player all enemies use.

    Variables:
        GRAVITY: the amount applied to the current gravity each frame.
        MAX_GRAVITY: the maximum gravity that can be applied.
        
        overrides: dictonary of the different override scenarios.

        cooldown_timers: base timers for player actions.
        cooldowns: ongoing cooldowns for player actions.

        gravity_info: information on the current values of the entity.
        state_info: information on the current state of the entity.

        default_movement_info: initial movement information of the entity.
        movement_info: ongoing movement information of the entity.
        default_combat_info: initial combat information of the entity.
        combat_info: ongoing combat information of the entity.

        buffs: list of buffs that the entity has.
        debuffs: list of debuffs that the entity has.

    Methods:
        apply_collision_x_default(): applies the default collision to the entity's x axis.
        apply_collision_x_default(): applies the default collision to the entity's y axis.
        apply_gravity(): applies gravity to the entity.

        set_gravity(): sets the current gravity of the entity for a set amount of frames.
        set_friction(): sets the entity friction temporarily.

        get_stat(): returns a value of either the combat dictionary or the movement dictionary.
        set_stat(): sets a value of either the combat dictionary or the movement dictionary.

        set_frame_state(): sets the frame state of the player depending on movement.
    '''

    GRAVITY = 2
    MAX_GRAVITY = 30

    def __init__(self, position, img, dimensions, strata, alpha=None):
        super().__init__(position, img, dimensions, strata, alpha)
        
        self.overrides = {}

        self.gravity_info = {
            'frames': 0,
            'gravity': self.GRAVITY,
            'max_gravity': self.MAX_GRAVITY
        }

        self.state_info = {
            'dead': 0,
            'movement': None
        }

        self.cooldown_timers = {
            'jump': 8
        }

        self.cooldowns = {}
        for cd in self.cooldown_timers.keys():
            self.cooldowns[cd] = 0

        self.default_movement_info = {
            'direction': 0,

            'friction': .75,
            'friction_frames': 0,

            'per_frame_movespeed': 3,
            'max_movespeed': 12,

            'jump_power': 24,
            'jumps': 0,
            'max_jumps': 2
        }

        self.movement_info = self.default_movement_info.copy()

        self.default_combat_info = {
            'max_health': 100,
            'health': 100,

            'health_regen_amount': .01,
            'health_regen_tick': 60,
            'health_regen_timer': 0,

            'damage_multiplier': 1.0,
            'healing_multiplier': 1.0,

            'base_damage': 25,
            'crit_strike_chance': .15,
            'crit_strike_multiplier': 1.5,

            'knockback_resistance': 1,

            'immunities': get_immunity_dict(),
            'mitigations': get_mitigation_dict()
        }
        
        self.combat_info = self.default_combat_info.copy()

        self.buffs = []
        self.debuffs = []

    def apply_collision_x_default(self, collidables):
        callback_collision = []

        for collidable in collidables:
            if collidable.secondary_sprite_id == 'barrier':
                if self.sprite_id not in collidable.sprite_ids:
                    continue

            if not self.rect.colliderect(collidable.rect):
                if collidable in self.collision_ignore:
                    self.collision_ignore.remove(collidable)
                
                if collidable in self.collisions:
                    self.collisions.remove(collidable)

                continue

            if collidable in self.collision_ignore:
                continue

            if self.velocity[0] > 0:
                self.rect.right = collidable.rect.left
                self.collide_points['right'] = True

                callback_collision.append('right')

                if collidable not in self.collisions:
                    self.collisions.append(collidable)
       
                self.velocity[0] = 0

            if self.velocity[0] < 0:
                self.rect.left = collidable.rect.right
                self.collide_points['left'] = True

                if collidable not in self.collisions:
                    self.collisions.append(collidable)

                callback_collision.append('left')
                self.velocity[0] = 0

        return callback_collision

    def apply_collision_y_default(self, collidables):
        callback_collision = []

        for collidable in collidables:
            if collidable.secondary_sprite_id == 'barrier':
                if self.sprite_id not in collidable.sprite_ids:
                    continue

            if not self.rect.colliderect(collidable.rect):
                if collidable in self.collision_ignore:
                    self.collision_ignore.remove(collidable)

                if collidable in self.collisions:
                    self.collisions.remove(collidable)
                    
                continue

            if collidable in self.collision_ignore:
                continue

            if abs(self.velocity[1]) < 0:
                return

            top = abs(self.rect.top - collidable.rect.centery)
            bottom = abs(self.rect.bottom - collidable.rect.centery)
            
            if top < bottom and collidable.secondary_sprite_id != 'floor':
                self.rect.top = collidable.rect.bottom
                self.collide_points['top'] = True

                callback_collision.append('top')

                if collidable not in self.collisions:
                    self.collisions.append(collidable)
                    
                self.velocity[1] = 0

            elif collidable.secondary_sprite_id != 'ceiling':
                self.rect.bottom = collidable.rect.top
                self.collide_points['bottom'] = True

                callback_collision.append('bottom')

                if collidable not in self.collisions:
                    self.collisions.append(collidable)

                self.velocity[1] = 0

        return callback_collision  

    def apply_gravity(self, dt, multiplier=1.0):
        grav = self.gravity_info['gravity']
        max_grav = self.gravity_info['max_gravity']
        
        if dt == 0:
            self.velocity[1] = 0

        elif dt <= .5 and self.collide_points['bottom']:
            self.velocity[1] += (grav / dt) * multiplier

        else: 
            self.velocity[1] += (grav * dt if self.velocity[1] < max_grav * dt else 0) * multiplier

    def get_stat(self, stat):
        if stat in self.combat_info:
            return self.combat_info[stat]
        
        elif stat in self.movement_info:
            return self.movement_info[stat]

    def set_stat(self, stat, value, additive=False):
        if stat in self.combat_info: 
            if additive:
                self.combat_info[stat] += value
            else:
                self.combat_info[stat] = value

            return self.combat_info[stat]
        
        elif stat in self.movement_info:
            if additive:
                self.movement_info[stat] += value
            else:
                self.movement_info[stat] = value

            return self.movement_info[stat]

    def set_gravity(self, frames, grav=None, max_grav=None):
        if grav is None:
            grav = Entity.GRAVITY

        if max_grav is None:
            max_grav = Entity.MAX_GRAVITY

        self.gravity_info['frames'] = frames
        self.gravity_info['gravity'] = grav
        self.gravity_info['max_gravity'] = max_grav

    def set_friction(self, frames, friction):
        self.movement_info['friction_frames'] = frames
        self.movement_info['friction'] = friction

    def set_frame_state(self):
        if not self.collide_points['bottom']:
            if self.velocity[1] < 0:
                self.state_info['movement'] = 'jump'
                return

            else:
                self.state_info['movement'] = 'fall'
                return

        if self.velocity[0] > 0 or self.velocity[0] < 0:
            self.state_info['movement'] = 'run'
            return

        self.state_info['movement'] = 'idle'

    def display(self, scene, dt):
        for event in self.cooldowns.keys():
            if self.cooldowns[event] < 1 * dt:
                self.cooldowns[event] = 0
                continue

            self.cooldowns[event] -= 1 * dt

        if self.gravity_info['frames'] > 0:
            self.gravity_info['frames'] -= 1 * dt

        elif self.gravity_info['frames'] <= 0:
            if self.gravity_info['gravity'] != self.GRAVITY or self.gravity_info['max_gravity'] != self.MAX_GRAVITY:
                self.gravity_info = {
                    'frames': 0,
                    'gravity': self.GRAVITY,
                    'max_gravity': self.MAX_GRAVITY
                }

        for buff in self.buffs:
            buff.update(scene, dt)
        
        for debuff in self.debuffs:
            debuff.update(scene, dt)

        if self.movement_info['friction_frames'] > 0:
            self.movement_info['friction_frames'] -= 1 * dt

        elif self.movement_info['friction_frames'] <= 0:
            if self.movement_info['friction'] != self.default_movement_info['friction']:
                self.movement_info['friction'] = self.default_movement_info['friction']
                self.movement_info['friction_frames'] = 0

        if self.combat_info['health_regen_amount'] > 0:
            self.combat_info['health_regen_timer'] += 1 * dt
            if self.combat_info['health_regen_timer'] >= self.combat_info['health_regen_tick']:
                self.combat_info['health_regen_timer'] = 0

                if self.combat_info['health'] < self.combat_info['max_health']:
                    register_heal(
                        scene,
                        self, 
                        {'type': 'passive', 'amount': self.combat_info['max_health'] * self.combat_info['health_regen_amount']}
                    )

        if self.combat_info['health'] > self.combat_info['max_health']:
            self.combat_info['health'] = self.combat_info['max_health']

        self.combat_info['crit_strike_chance'] = round(self.combat_info['crit_strike_chance'], 2)
        
        for immunity in self.combat_info['immunities'].keys():
            if '&' in immunity or self.combat_info['immunities'][immunity] == 0:
                continue

            if self.combat_info['immunities'][immunity] < 0:
                self.combat_info['immunities'][immunity] = 0
                continue

            self.combat_info['immunities'][immunity] -= 1 * dt

        del_list = []
        for mitigation in self.combat_info['mitigations']:
            if '&' in mitigation:
                continue
        
            for name, values in self.combat_info['mitigations'][mitigation].items():
                if values[1] <= 0:
                    del_list.append([mitigation, name])
                    continue

                self.combat_info['mitigations'][mitigation][name][1] -= 1 * dt

        for item in del_list:
            del self.combat_info['mitigations'][item[0]][item[1]]

        super().display(scene, dt)
        