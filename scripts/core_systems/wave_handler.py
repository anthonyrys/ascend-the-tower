'''
Holds the WaveHandler class.
'''

from scripts.constants import SCREEN_DIMENSIONS

from scripts.entities.enemy import RockGolem, StoneSentry, GraniteElemental

import pygame
import random
import math

class WaveHandler:
    '''
    Handles enemy spawning calculations via waves and areas.

    Variables:
        MAX_AREAS: the maximum amount of areas the game current has.
        MAX_WAVES: the maximum amount of waves each area should have.

        ENEMY_INFO: list of enemies that spawn during each area.
        camera_offset: the value by which the sprite surface should be offset by.

        scene: the current scene.

        area: the current area.
        wave: the current wave.
        level: the current wave (does not get wiped per area).

        floor: the current floor (increases every 3 waves or every boss).

        area_info: information on the current area.
        wave_info: information on the current wave.
        floor_info: information on the current floor.

    Methods:
        get_wave_count(): gets the amount of enemies depending on the wave.
        get_enemy_level(): gets the level of the enemies depending on the current level.
        
        get_spawn_position(): returns the location of the enemy spawn position.
        
        on_area_complete(): calls once an area has been completed; calls new_area().
        on_wave_complete(): calls once a wave has been completed; resets wave_info, removes all enemies, and calls scene on_wave_complete().

        on_enemy_spawn(): calls once a enemy has been spawned; adds to the count value of wave_info.
        on_enemy_death(): calls once a enemy has been defeated; subtracts from the count value of wave_info.

        new_area(): sets the current wave to 0, and creates a dictionary for the waves of the area. 
        new_wave(): adds to the current wave and level, and grabs new wave information from area_info.

        update(): called every frame.
    '''

    MAX_AREAS = 1
    MAX_WAVES = 9

    ENEMY_INFO = {
        1: [RockGolem, StoneSentry, GraniteElemental]
    }

    @staticmethod
    def get_wave_count(area, wave):
        return round((math.pow(wave, 1.26) + 4) * area)

    @staticmethod
    def get_enemy_level(level):
        return math.ceil(level * .5)

    def __init__(self, scene):
        self.scene = scene

        self.area = 1

        self.wave = 0
        self.level = self.wave

        self.floor = 1

        self.spawn_rect = None

        self.area_info = {}
        self.wave_info = {}
        self.floor_info = [0, 3, 0]

    def get_spawn_position(self):
        direction = 1 if random.random() < 0.5 else -1

        y = self.scene.tiles['floor'][0].rect.y - 100

        x = self.scene.player.rect.centerx + ((SCREEN_DIMENSIONS[0]) * direction)
        if not self.spawn_rect.collidepoint(x, y):
            x = self.scene.player.rect.centerx + ((SCREEN_DIMENSIONS[0]) * -direction)

        return [x, y]
        
    def on_area_complete(self):
        self.new_area()

    def on_wave_complete(self):
        self.floor_info[0] += 1
        
        if self.floor_info[0] >= self.floor_info[1]:
            self.floor_info[0] = 0

            self.floor_info[2] += 1
            self.floor += 1
        
        # MINI_BOSS
        if self.floor_info[2] == 2:
            # spawn mini_boss
            self.floor_info[2] += 1
            self.floor += 1

        # BOSS
        elif self.floor_info[2] == 4:
            # spawn boss
            self.floor += 1
            self.on_area_complete()
        
        self.wave_info = {}
        
        for enemy in [e for e in self.scene.sprites if e.sprite_id == 'enemy']:
            enemy.on_death(self.scene, None)

        self.scene.delay_timers.append([45, self.scene.on_wave_complete, []])

    def on_enemy_spawn(self):
        if not self.wave_info:
            return

        self.wave_info['count'][0] += 1
        self.wave_info['count'][1] += 1

    def on_enemy_death(self):
        if not self.wave_info:
            return

        self.wave_info['count'][0] -= 1

    def new_area(self):
        # self.level += 1
        self.wave = 0
        self.floor_info[2] = 0

        for i in range(self.MAX_WAVES):
            self.area_info[i + 1] = {}
            
            self.area_info[i + 1]['enemies'] = []
            for _ in range(round(len(self.ENEMY_INFO[self.area]) * ((i + 2) / self.MAX_WAVES))):
                self.area_info[i + 1]['enemies'].append(self.ENEMY_INFO[self.area][_])

            count = self.get_wave_count(self.area, i + 1)
            
            # [enemies alive, total enemies spawned, enemies allowed at once, total enemies allowed to spawn]
            self.area_info[i + 1]['count'] = [0, 0, round(count * .4), count]
            self.area_info[i + 1]['rate'] = [0, 60]

    def new_wave(self):
        self.wave += 1
        self.level += 1

        self.wave_info = self.area_info[self.wave].copy()

    def update(self, dt):
        if not self.wave_info:
            return

        # print(f'{self.area}: {self.level}; {self.wave}, {self.wave_info}')
        
        if self.wave_info['count'][1] >= self.wave_info['count'][3]:
            if self.wave_info['count'][0] <= 0:
                self.on_wave_complete()

            return

        if self.wave_info['count'][0] >= self.wave_info['count'][2]:
            return
        
        self.wave_info['rate'][0] += 1 * dt
        if self.wave_info['rate'][0] < self.wave_info['rate'][1]:
            return
        
        self.wave_info['rate'][0] = 0

        enemy = random.choice(self.wave_info['enemies'])(self.get_spawn_position(), 6, level=self.get_enemy_level(self.level))

        self.scene.add_sprites(enemy)
        self.scene.on_enemy_spawn()
