'''
File that holds StatusEffect baseclass as well as StatusEffect subclasses.
'''

import pygame

def get_buff(entity, signature):
    buff_list = []
    for buff in entity.buffs:
        if buff.signature != signature:
            continue

        buff_list.append(buff)

    if len(buff_list) == 1:
        return buff_list[0]
    
    return buff_list

def get_debuff(entity, signature):
    debuff_list = []
    for debuff in entity.debuffs:
        if debuff.signature != signature:
            continue

        debuff_list.append(debuff)

    if len(debuff_list) == 1:
        return debuff_list[0]

    return debuff_list

class StatusEffect:
    '''
    StatusEffect baseclass that is meant to be inherited from.

    Variables:
        entity: the entity object
        signature: a unique string used to identify status effects

        duration: duration of the status effect.
        stat: the stat that is being affected.
        value: value of much the stat is being affected.

    Methods:
        update: updates the status effect every frame.
        apply: applies the status effect onto the entity's stats.
        end: returns the entity's stats prior to applying.
    '''

    STATUS_EFFECT_TYPE = None 

    def __init__(self, entity, signature, stat, value, duration):
        self.entity = entity
        self.signature = signature

        self.duration = duration
        self.stat = stat
        self.value = value

        self.apply()
        
    def update(self, scene, dt):
        if self.duration is None:
            return
        
        self.duration -= 1 * dt
        if self.duration < 0:
            self.end()

    def apply(self):
        self.entity.set_stat(self.stat, self.value, True)

    def end(self):
        self.entity.set_stat(self.stat, -self.value, True)

class Buff(StatusEffect):
    STATUS_EFFECT_TYPE = 'buff' 

    def __init__(self, entity, signature, stat, value, duration):
        super().__init__(entity, signature, stat, value, duration)

    def end(self):
        if self in self.entity.buffs:
            self.entity.buffs.remove(self)

        super().end()

class Debuff(StatusEffect):
    STATUS_EFFECT_TYPE = 'debuff' 

    def __init__(self, entity, signature, stat, value, duration):
        super().__init__(entity, signature, stat, value, duration)

    def end(self):
        if self in self.entity.debuffs:
            self.entity.debuffs.remove(self)

        super().end()
