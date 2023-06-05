'''
File that holds Talent baseclass as well as talent subclasses.
'''

from scripts.constants import HEAL_COLOR, PLAYER_COLOR
from scripts.engine import get_distance, Entity

from scripts.core_systems.combat_handler import register_heal, register_damage
from scripts.core_systems.status_effects import get_buff, get_debuff, Buff, Debuff, OnFire

from scripts.entities.particle_fx import Image, Circle

from scripts.ui.card import Card
from scripts.ui.text_box import TextBox

import pygame
import inspect
import random
import sys
import math
import os

def get_all_talents():
	talent_list = []
	for talent in inspect.getmembers(sys.modules[__name__], inspect.isclass):
		if not issubclass(talent[1], Talent) or talent[1].TALENT_ID is None:
			continue
			
		talent_list.append(talent[1])
			
	return talent_list

def get_talent(player, talent_id):
	for talent in player.talents:
		if talent.TALENT_ID != talent_id:
			continue

		return talent
	
def call_talents(scene, player, calls):
	for call, info in calls.items():
		for talent in player.talents:
			if call not in talent.TALENT_CALLS:
				continue
				
			talent.call(call, scene, info)

def reset_talents(player):
	for talent in player.talents:
		talent.reset()

class Talent:
	'''
    Talent baseclass that is meant to be inherited from.

    Variables:
        DRAW_TYPE: used to distinguish between card types.
        DRAW_SPECIAL: used to determine how a card is created.
        TALENT_ID: the id of the talent.
		TALENT_CALLS: list of strings that is used to call specific talents.
        DESCRIPTION: the description of the talent; used for card creation.

        player: the player object.
        overrides: if the player should be overriden by the talent.

        talent_info: used for custom talent functions.

    Methods:
        fetch(): returns the card info.
        check_draw_condition(): returns whether the talent is able to be drawn.

        call(): calls the talent to activate depending on TALENT_CALLS. 
        reset(): resets the talent to its pre-call() state.
        update(): update the object every frame.
    '''

	DRAW_TYPE = 'TALENT'
	DRAW_SPECIAL = None

	TALENT_ID = None
	TALENT_CALLS = []

	DESCRIPTION = {
		'name': None,
		'description': None
	}

	def __init__(self, scene, player):
		self.player = player
		self.overrides = False
		
		self.talent_info = {
            'cooldown_timer': 0,
            'cooldown': 0
		}
		
	@staticmethod
	def fetch():
		card_info = {
			'type': 'talent',
			
			'icon': None,
			'symbols': []
		}

		return card_info
	
	@staticmethod
	def check_draw_condition(player):
		return True

	def call(self, call, scene, info=None):
		# print(f'{self.TALENT_ID}::call({call})')
		...

	def reset(self):
		...

	def update(self, scene, dt):
		if self.talent_info['cooldown'] > 0:
			self.talent_info['cooldown'] -= 1 * dt

class Vampirism(Talent):
	TALENT_ID = 'vampirism'
	TALENT_CALLS = ['on_@primary_attack']

	DESCRIPTION = {
		'name': 'Vampirism',
		'description': 'Heal a portion of the damage your primary attack deals.'
	}

	@staticmethod
	def fetch():
		card_info = {
			'type': 'talent',
			
			'icon': 'vampirism',
			'symbols': [
				Card.SYMBOLS['type']['talent'],
				Card.SYMBOLS['action']['heal'],
				Card.SYMBOLS['talent']['attack/kill']
			]
		}

		return card_info

	def __init__(self, scene, player):
		super().__init__(scene, player)

		self.talent_info['heal_amount'] = 0.1

		if self.player.abilities['primary']:
			self.player.abilities['primary'].ability_info['color'] = (255, 125, 125)

	def call(self, call, scene, info):
		super().call(call, scene, info)

		register_heal(scene, self.player, {'type': 'status', 'amount': info['amount'] * self.talent_info['heal_amount']})

class ComboStar(Talent):
	TALENT_ID = 'combo_star'
	TALENT_CALLS = ['on_player_attack']

	DESCRIPTION = {
		'name': 'Combo Star',
		'description': 'Deal additional damage when chaining your attacks in quick succession.'
	}

	@staticmethod
	def fetch():
		card_info = {
			'type': 'talent',
			
			'icon': 'combo-star',
			'symbols': [
				Card.SYMBOLS['type']['talent'],
				Card.SYMBOLS['action']['damage'],
				Card.SYMBOLS['talent']['attack/kill']
			]
		}

		return card_info

	def __init__(self, scene, player):
		super().__init__(scene, player)

		self.talent_info['multiplier'] = 0
		self.talent_info['per_multiplier'] = .1
		self.talent_info['multiplier_cap'] = .5

		self.talent_info['decay_time'] = 45
		self.talent_info['time'] = 0

		self.talent_info['buff_signature'] = 'combo_star'

	def call(self, call, scene, info):
		super().call(call, scene, info)

		self.talent_info['time'] = self.talent_info['decay_time']
		if self.talent_info['multiplier'] < self.talent_info['multiplier_cap']:
			self.talent_info['multiplier'] = round(self.talent_info['multiplier'] + self.talent_info['per_multiplier'], 2)

		current_buff = get_buff(self.player, self.talent_info['buff_signature'])
		if current_buff:
			current_buff.end()

		buff = Buff(self.player, self.talent_info['buff_signature'], 'damage_multiplier', self.talent_info['multiplier'], self.talent_info['decay_time'])
		self.player.buffs.append(buff)

	def update(self, scene, dt):
		if self.talent_info['time'] <= 0 and self.talent_info['multiplier'] != 0:
			self.talent_info['multiplier'] = 0

		elif self.talent_info['time'] > 0:
			self.talent_info['time'] -= 1 * dt

class FloatLikeAButterfly(Talent):
	TALENT_ID = 'float_like_a_butterfly'

	DESCRIPTION = {
		'name': 'Float Like A Butterfly',
		'description': 'Gain an additional jump.'
	}

	@staticmethod
	def fetch():
		card_info = {
			'type': 'talent',
			
			'icon': 'float-like-a-butterfly',
			'symbols': [
				Card.SYMBOLS['type']['talent'],
				Card.SYMBOLS['action']['other'],
				Card.SYMBOLS['talent']['passive']
			]
		}

		return card_info
	
	def __init__(self, scene, player):
		super().__init__(scene, player)

		jump_buff = Buff(self.player, self.TALENT_ID, 'max_jumps', 1, None)
		self.player.buffs.append(jump_buff)

class StingLikeABee(Talent):
	TALENT_ID = 'sting_like_a_bee'
	TALENT_CALLS = ['on_player_kill']

	DESCRIPTION = {
		'name': 'Sting Like A Bee',
		'description': 'Defeating an enemy resets your jumps.'
	}

	@staticmethod
	def fetch():
		card_info = {
			'type': 'talent',
			
			'icon': 'sting-like-a-bee',
			'symbols': [
				Card.SYMBOLS['type']['talent'],
				Card.SYMBOLS['action']['cooldown'],
				Card.SYMBOLS['talent']['attack/kill']
			]
		}

		return card_info

	@staticmethod
	def check_draw_condition(player):
		if get_talent(player, 'float_like_a_butterfly'):
			return True
		
		return False
		
	def __init__(self, scene, player):
		super().__init__(scene, player)

	def call(self, call, scene, info):
		super().call(call, scene, info)

		self.player.set_stat('jumps', self.player.get_stat('max_jumps'), False)

class Marksman(Talent):
	TALENT_ID = 'marksman'
	TALENT_CALLS = ['on_@primary_collide']

	DESCRIPTION = {
		'name': 'Marksman',
		'description': 'Your primary attack deals more damage the farther your target is.'
	}
	
	@staticmethod
	def fetch():
		card_info = {
			'type': 'talent',
			
			'icon': 'marksman',
			'symbols': [
				Card.SYMBOLS['type']['talent'],
				Card.SYMBOLS['action']['damage'],
				Card.SYMBOLS['talent']['ability']
			]
		}

		return card_info

	def __init__(self, scene, player):
		super().__init__(scene, player)

		self.talent_info['min_distance'] = 300
		self.talent_info['per_damage_distance_ratio'] = [.1, 75]
		self.talent_info['max_distance'] = False

	def call(self, call, scene, info):
		distance = get_distance(info.start, self.player.center_position)
		if distance < self.talent_info['min_distance']:
			return
		
		super().call(call, scene, info)

		distance = round(distance / self.talent_info['per_damage_distance_ratio'][1])
		info.ability_info['damage'] *= round(distance * self.talent_info['per_damage_distance_ratio'][0], 2) + 1

class Temperance(Talent):
	class TemperanceHalo(Entity):
		def __init__(self, strata):
			img = pygame.image.load(os.path.join('imgs', 'entities', 'visuals', 'temperance.png')).convert_alpha()
			img_scale = 1.5

			img = pygame.transform.scale(img, (img.get_width() * img_scale, img.get_height() * img_scale)).convert_alpha()
			img.set_colorkey((0, 0, 0))

			super().__init__((0, 0), img, None, strata)

			self.glow['active'] = True
			self.glow['size'] = 1.2
			self.glow['intensity'] = .4

			self.sin_amplifier = 1
			self.sin_frequency = .05

			self.sin_count = 0

		def display(self, player, scene, dt):
			self.rect.centerx = player.rect.centerx
			self.rect.centery = player.rect.top - 17 - round((self.sin_amplifier * math.sin(self.sin_frequency * (self.sin_count))))
			
			self.sin_count += 1 * dt

			super().display(scene, dt)

	TALENT_ID = 'temperance'

	DESCRIPTION = {
		'name': 'Temperance',
		'description': 'You can no longer critical strike but gain a permanent damage increase.'
	}

	def __init__(self, scene, player):
		super().__init__(scene, player)

		self.talent_info['damage_multiplier'] = 0.75

		damage_buff = Buff(self.player, 'temperance', 'damage_multiplier', self.talent_info['damage_multiplier'], None)
		crit_chance_debuff = Debuff(self.player, 'temperance', 'crit_strike_chance', -100, None)

		self.player.buffs.append(damage_buff)
		self.player.debuffs.append(crit_chance_debuff)

		self.player.visuals.append(self.TemperanceHalo(self.player.strata))
		
	@staticmethod
	def fetch():
		card_info = {
			'type': 'talent',
			
			'icon': 'temperance',
			'symbols': [				
				Card.SYMBOLS['type']['talent'],
				Card.SYMBOLS['action']['other'],
				Card.SYMBOLS['talent']['passive']
			]
		}

		return card_info

class WheelOfFortune(Talent):
	TALENT_ID = 'wheel_of_fortune'

	DESCRIPTION = {
		'name': 'Wheel of Fortune',
		'description': 'Periodically gain a buff to a random stat.'
	}

	@staticmethod
	def fetch():
		card_info = {
			'type': 'talent',
			
			'icon': 'wheel-of-fortune',
			'symbols': [				
				Card.SYMBOLS['type']['talent'],
				Card.SYMBOLS['action']['other'],
				Card.SYMBOLS['talent']['passive']
			]
		}

		return card_info

	def __init__(self, scene, player):
		super().__init__(scene, player)

		self.talent_info['stats'] = {
			'max_health': .2,
			'base_damage': .2,
			'crit_strike_chance': .5,
			'crit_strike_multiplier': .5,
			'max_movespeed': .25
		}

		self.talent_info['names'] = {
			'max_health': 'health',
			'base_damage': 'damage',
			'crit_strike_chance': 'crit chance',
			'crit_strike_multiplier': 'crit multiplier',
			'max_movespeed': 'speed'
		}

		self.talent_info['current_stat'] = None
		
		self.talent_info['buff_signature'] = 'wheel_of_fortune'
		self.talent_info['cooldown_timer'] = 300

	def display_text(self, scene, stat):
		img = TextBox((0, 0), '+ ' + self.talent_info['names'][stat], color=HEAL_COLOR, size=.5).image.copy()
		particle = Image(self.player.rect.center, img, 6, 255)
		particle.set_easings(alpha='ease_in_quint')
		particle.set_goal(
			60, 
			position=(self.player.rect.centerx, particle.rect.centery + random.randint(-100, -50)),
			alpha=0,
			dimensions=(img.get_width(), img.get_height())
		)

		scene.add_sprites(particle)

	def update(self, scene, dt):
		super().update(scene, dt)

		if self.talent_info['cooldown'] > 0:
			return
		
		self.talent_info['cooldown'] = self.talent_info['cooldown_timer']

		has_temperance = get_talent(self.player, 'temperance')

		stat = random.choice(list(self.talent_info['stats'].keys()))

		while stat == self.talent_info['current_stat']:
			stat = random.choice(list(self.talent_info['stats'].keys()))

		if has_temperance:
			while stat in ['crit_strike_chance', 'crit_strike_multiplier']:
				stat = random.choice(list(self.talent_info['stats'].keys()))

		health_proportion = self.player.get_stat('health') / self.player.get_stat('max_health')

		current_buff = get_buff(self.player, self.talent_info['buff_signature'])
		if current_buff:
			current_buff.end()

		val = self.player.get_stat(stat) * self.talent_info['stats'][stat]
		val = round(val) if stat not in ['crit_strike_multiplier', 'crit_strike_chance'] else round(val, 2)

		buff = Buff(self.player, self.talent_info['buff_signature'], stat, val, None)

		self.player.buffs.append(buff)
		self.player.set_stat('health', round(self.player.get_stat('max_health') * health_proportion))

		self.display_text(scene, stat)
		self.talent_info['current_stat'] = stat
	
class Recuperation(Talent):
	TALENT_ID = 'recuperation'
	TALENT_CALLS = ['on_player_damaged']

	DESCRIPTION = {
		'name': 'Recuperation',
		'description': 'Gain increased health regeneration upon taking damage.'
	}

	@staticmethod
	def fetch():
		card_info = {
			'type': 'talent',
			
			'icon': 'recuperation',
			'symbols': [				
				Card.SYMBOLS['type']['talent'],
				Card.SYMBOLS['action']['heal'],
				Card.SYMBOLS['talent']['hurt/death']
			]
		}

		return card_info
	
	def __init__(self, scene, player):
		super().__init__(scene, player)

		self.talent_info['tick_reduction'] = 50

		self.talent_info['buff_duration'] = 60
		self.talent_info['buff_signature'] = 'recuperation'

	def call(self, call, scene, info):
		super().call(call, scene, info)

		current_buff = get_buff(self.player, self.talent_info['buff_signature'])
		if current_buff:
			current_buff.duration = self.talent_info['buff_duration']
			return
		
		buff = Buff(self.player, self.talent_info['buff_signature'], 'health_regen_tick', -self.talent_info['tick_reduction'], self.talent_info['buff_duration'])
		self.player.buffs.append(buff)

class Holdfast(Talent):
	TALENT_ID = 'holdfast'
	TALENT_CALLS = ['on_player_damaged']

	DESCRIPTION = {
		'name': 'Holdfast',
		'description': 'Taking damage will temporarily apply a resistance towards that type of damage.'
	}

	@staticmethod
	def fetch():
		card_info = {
			'type': 'talent',
			
			'icon': 'holdfast',
			'symbols': [				
				Card.SYMBOLS['type']['talent'],
				Card.SYMBOLS['action']['resistance/immunity'],
				Card.SYMBOLS['talent']['hurt/death']
			]
		}

		return card_info
	
	def __init__(self, scene, player):
		super().__init__(scene, player)

		self.talent_info['mitigation_amount'] = .5
		self.talent_info['mitigation_time'] = 60
	
	def call(self, call, scene, info):
		super().call(call, scene, info)

		self.player.combat_info['mitigations'][info['type']][self.TALENT_ID] = [self.talent_info['mitigation_amount'], self.talent_info['mitigation_time']]

class GuardianAngel(Talent):
	TALENT_ID = 'guardian_angel'
	TALENT_CALLS = ['on_player_death']

	DESCRIPTION = {
		'name': 'Guardian Angel',
		'description': 'Upon taking fatal damage you heal a portion of your max health. Can only occur once.'
	}

	@staticmethod
	def fetch():
		card_info = {
			'type': 'talent',
			
			'icon': 'guardian-angel',
			'symbols': [				
				Card.SYMBOLS['type']['talent'],
				Card.SYMBOLS['action']['heal'],
				Card.SYMBOLS['talent']['hurt/death']
			]
		}

		return card_info
	
	def __init__(self, scene, player):
		super().__init__(scene, player)

		self.talent_info['charges'] = 1
	
	def call(self, call, scene, info):
		if self.talent_info['charges'] <= 0:
			return
		
		super().call(call, scene, info)

		heal_amount = self.player.combat_info['max_health'] * .25
		register_heal(scene, self.player, {'type': 'status', 'amount': heal_amount, 'color': PLAYER_COLOR, 'offset': [50, 0]})
		
		self.player.img_info['pulse_frames'] = 45
		self.player.img_info['pulse_frames_max'] = 45
		self.player.img_info['pulse_frame_color'] = PLAYER_COLOR

		self.talent_info['charges'] -= 1

class ChainReaction(Talent):
	TALENT_ID = 'chain_reaction'
	TALENT_CALLS = ['on_@primary_attack']

	DESCRIPTION = {
		'name': 'Chain Reaction',
		'description': 'Your primary attack will chain up to 3 times around your target.'
	}

	@staticmethod
	def fetch():
		card_info = {
			'type': 'talent',
			
			'icon': 'chain-reaction',
			'symbols': [				
				Card.SYMBOLS['type']['talent'],
				Card.SYMBOLS['action']['damage'],
				Card.SYMBOLS['talent']['attack/kill']
			]
		}

		return card_info
	
	def __init__(self, scene, player):
		super().__init__(scene, player)

		self.talent_info['charges'] = 3
		self.talent_info['range'] = 150
		self.talent_info['damage_percentage'] = .5
	
	def call(self, call, scene, info):
		super().call(call, scene, info)
	
		charges = self.talent_info['charges']
		target = info['target']
		enemies = []

		for sprite in [s for s in scene.sprites if s.sprite_id == 'enemy' and s != target]:
			if charges <= 0:
				break
			
			if get_distance(target, sprite) > self.talent_info['range']:
				continue

			if sprite in enemies:
				continue

			enemies.append(sprite)
			charges -= 1

		for enemy in enemies:
			info = register_damage(
				scene,
				self.player,
				enemy,
				{'type': info['type'], 'amount': info['amount'] * self.talent_info['damage_percentage']}
			)

			self.player.on_attack(scene, info)

class Bloodlust(Talent):
	TALENT_ID = 'bloodlust'
	TALENT_CALLS = ['on_player_kill']

	DESCRIPTION = {
		'name': 'Bloodlust',
		'description': 'Defeating an enemy grants a temporary speed and damage buff.'
	}

	@staticmethod
	def fetch():
		card_info = {
			'type': 'talent',
			
			'icon': 'bloodlust',
			'symbols': [				
				Card.SYMBOLS['type']['talent'],
				Card.SYMBOLS['action']['other'],
				Card.SYMBOLS['talent']['attack/kill']
			]
		}

		return card_info

	def __init__(self, scene, player):
		super().__init__(scene, player)
		
		self.talent_info['buff_duration'] = 60
		self.talent_info['buff_signature'] = 'bloodlust'

		self.talent_info['damage_buff'] = .1
		self.talent_info['speed_buff'] = 3

	def call(self, call, scene, info):
		current_buffs = get_buff(self.player, self.talent_info['buff_signature'])
		if current_buffs:
			for current_buff in current_buffs:
				current_buff.duration = self.talent_info['buff_duration']

			return
		
		damage_buff = Buff(self.player, self.talent_info['buff_signature'], 'damage_multiplierr', self.talent_info['damage_buff'], self.talent_info['buff_duration'])
		speed_buff = Buff(self.player, self.talent_info['buff_signature'], 'max_movespeed', self.talent_info['speed_buff'], self.talent_info['buff_duration'])

		self.player.buffs.extend([damage_buff, speed_buff])

class Ignition(Talent):
	TALENT_ID = 'ignition'
	TALENT_CALLS = ['on_player_attack']

	DESCRIPTION = {
		'name': 'Ignition',
		'description': 'Your attacks sets enemies ablaze.'
	}

	@staticmethod
	def fetch():
		card_info = {
			'type': 'talent',
			
			'icon': 'ignition',
			'symbols': [				
				Card.SYMBOLS['type']['talent'],
				Card.SYMBOLS['action']['damage'],
				Card.SYMBOLS['talent']['attack/kill']
			]
		}

		return card_info
	
	def __init__(self, scene, player):
		super().__init__(scene, player)

		self.talent_info['signature'] = 'ignition'

		self.talent_info['duration'] = 30
		self.talent_info['damage_percentage'] = .5

	def call(self, call, scene, info):
		super().call(call, scene, info)
		has_debuff = get_debuff(info['target'], self.talent_info['signature'])

		if has_debuff:
			has_debuff.duration = self.talent_info['duration']
			return
		
		damage = self.player.combat_info['base_damage'] * self.talent_info['damage_percentage']
		debuff = OnFire(self.player, info['target'], self.talent_info['signature'], damage, self.talent_info['duration'])
		info['target'].debuffs.append(debuff)

class RunItBack(Talent):
	TALENT_ID = 'run_it_back'
	TALENT_CALLS = ['on_ability']

	DESCRIPTION = {
		'name': 'Run It Back',
		'description': 'Using an ability has a chance equal to your critcal strike to reset its cooldown.'
	}

	@staticmethod
	def fetch():
		card_info = {
			'type': 'talent',
			
			'icon': 'run-it-back',
			'symbols': [				
				Card.SYMBOLS['type']['talent'],
				Card.SYMBOLS['action']['cooldown'],
				Card.SYMBOLS['talent']['ability']
			]
		}

		return card_info
	
	def __init__(self, scene, player):
		super().__init__(scene, player)

	@staticmethod
	def check_draw_condition(player):
		if get_talent(player, 'temperance'):
			return False

		if [ability for ability in [a for a in player.abilities.values() if a] if ability.ABILITY_ID[0] != '@']:
			return True

		return False

	def call(self, call, scene, info):
		if info.ABILITY_ID[0] == '@':
			return

		if self.player.combat_info['crit_strike_chance'] <= 0 or round(random.uniform(0, 1), 2) > self.player.combat_info['crit_strike_chance']:
			return

		super().call(call, scene, info)
		
		info.ability_info['cooldown'] = 1

class EvasiveManeuvers(Talent):
	TALENT_ID = 'evasive_maneuvers'
	TALENT_CALLS = ['on_evasive_shroud_end']

	DESCRIPTION = {
		'name': 'Evasive Maneuvers',
		'description': 'Gain a temporary damage resistance after evasive shroud has ended.'
	}

	@staticmethod
	def fetch():
		card_info = {
			'type': 'talent',
			
			'icon': 'evasive-maneuvers',
			'symbols': [				
				Card.SYMBOLS['type']['talent'],
				Card.SYMBOLS['action']['resistance/immunity'],
				Card.SYMBOLS['talent']['ability']
			]
		}

		return card_info
	
	@staticmethod
	def check_draw_condition(player):
		if [ability for ability in [a for a in player.abilities.values() if a] if ability.ABILITY_ID == 'evasive_shroud']:
			return True
		
		return False
		
	def __init__(self, scene, player):
		super().__init__(scene, player)

		self.talent_info['mitigation_time'] = 60
		self.talent_info['mitigation_amount'] = .25

		self.talent_info['particle_timer'] = [0, 15]

	def update(self, scene, dt):
		super().update(scene, dt)

		if self.TALENT_ID not in self.player.combat_info['mitigations']['all']:
			return
		
		self.talent_info['particle_timer'][0] += 1 * dt

		if self.talent_info['particle_timer'][0] < self.talent_info['particle_timer'][1]:
			return
		
		self.talent_info['particle_timer'][0] = 0

		pos = self.player.center_position

		particles = []
		for _ in range(2):
			cir = Circle(pos, (255, 255, 255), 6, 0)
			cir.set_goal(
						60, 
						position=(pos[0] + random.randint(-25, 25), pos[1] + random.randint(-100, -25)), 
						radius=0, 
						width=0
					)

			particles.append(cir)

		scene.add_sprites(particles)

	def call(self, call, scene, info):
		super().call(call, scene, info)
		
		self.player.combat_info['mitigations']['all'][self.TALENT_ID] = [self.talent_info['mitigation_amount'], self.talent_info['mitigation_time']]