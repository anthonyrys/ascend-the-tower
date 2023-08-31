from scripts.core_systems.combat_handler import register_damage

from scripts.entities.particle_fx import Circle

import pygame
import random

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
    STATUS_EFFECT_TYPE = None 

    def __init__(self, entity, signature, stat, value, duration, dot):
        self.entity = entity
        self.signature = signature

        self.duration = duration
        self.stat = stat
        self.value = value

        self.dot = dot
        
        self.apply()
        
    def update(self, scene, dt):
        if self.duration is None:
            return
        
        self.duration -= 1 * dt
        if self.duration < 0:
            self.end()

    def apply(self):
        if self.dot:
            return

        self.entity.set_stat(self.stat, self.value, True)

    def end(self):
        if self.dot:
            return

        self.entity.set_stat(self.stat, -self.value, True)

class Buff(StatusEffect):
    STATUS_EFFECT_TYPE = 'buff' 

    def __init__(self, entity, signature, stat, value, duration, dot=False):
        super().__init__(entity, signature, stat, value, duration, dot)

    def end(self):
        if self in self.entity.buffs:
            self.entity.buffs.remove(self)

        super().end()

class Debuff(StatusEffect):
    STATUS_EFFECT_TYPE = 'debuff' 

    def __init__(self, entity, signature, stat, value, duration, dot=False):
        super().__init__(entity, signature, stat, value, duration, dot)

    def end(self):
        if self in self.entity.debuffs:
            self.entity.debuffs.remove(self)

        super().end()

class OnFire(Debuff):
    def __init__(self, primary_entity, entity, signature, value, duration, tick_rate=.2, size=7):
        super().__init__(entity, signature, 'health', value, duration, dot=True)

        self.primary_entity = primary_entity

        self.tick_rate = [0, round(duration * tick_rate)]
        self.per_damage = round(value * tick_rate)

        self.particle_color = (255, 144, 98)
        self.particle_rate = [0, 3]
        self.particle_size = size

    def update(self, scene, dt):
        super().update(scene, dt)

        self.particle_rate[0] += 1 * dt
        if self.particle_rate[0] >= self.particle_rate[1]:
            self.particle_rate[0] = 0

            pos = self.entity.center_position
            pos[0] += random.randint(-5, 5)
            pos[1] += random.randint(-15, 0)

            particle = Circle(pos, self.particle_color, self.particle_size, 0)
            particle.set_goal(60, position=[pos[0] + random.randint(-50, 50), pos[1] + random.randint(-75, 0)], radius=0, width=0)

            particle.glow['active'] = True
            particle.glow['size'] = 1.5
            particle.glow['intensity'] = .25

            scene.add_sprites(particle)

        self.tick_rate[0] += 1 * dt
        if self.tick_rate[0] >= self.tick_rate[1]:
            self.tick_rate[0] = 0
            register_damage(scene, self.primary_entity, self.entity, {'type': 'magical', 'amount': self.per_damage, 'minor': True, 'velocity': None})

class Slowed(Debuff):
    def __init__(self, entity, signature, value, duration):
        super().__init__(entity, signature, 'max_movespeed', -value, duration)

    def update(self, scene, dt):
        super().update(scene, dt)
