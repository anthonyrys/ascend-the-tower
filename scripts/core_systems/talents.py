'''
File that holds Talent baseclass as well as talent subclasses.
'''

from scripts.constants import HEAL_COLOR, PLAYER_COLOR
from scripts.engine import get_distance

from scripts.core_systems.combat_handler import register_heal, register_damage
from scripts.core_systems.status_effects import get_buff, Buff, Debuff

from scripts.entities.particle_fx import Image

from scripts.ui.card import Card
from scripts.ui.text_box import TextBox

import pygame
import inspect
import random
import math
import sys

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

		if self.DRAW_SPECIAL:
			if self.DRAW_SPECIAL[0] == 'tarot card':
				self.player.talent_info['has_tarot_card'] = True
		
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
	TALENT_CALLS = ['on_player_attack']

	DESCRIPTION = {
		'name': 'Vampirism',
		'description': 'Heal a portion of the damage you deal.'
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
	TALENT_CALLS = ['on_@dash']

	DESCRIPTION = {
		'name': 'Float Like A Butterfly',
		'description': 'Gain an empowered dash.'
	}

	@staticmethod
	def fetch():
		card_info = {
			'type': 'talent',
			
			'icon': 'float-like-a-butterfly',
			'symbols': [
				Card.SYMBOLS['type']['talent'],
				Card.SYMBOLS['action']['speed'],
				Card.SYMBOLS['talent']['ability']
			]
		}

		return card_info
	
	def call(self, call, scene, info):
		super().call(call, scene, info)
		self.player.set_friction(30, .5)

class StingLikeABee(Talent):
	TALENT_ID = 'sting_like_a_bee'

	DESCRIPTION = {
		'name': 'Sting Like A Bee',
		'description': 'Gain additional critical strike chance when you have a speed boost.'
	}

	@staticmethod
	def fetch():
		card_info = {
			'type': 'talent',
			
			'icon': 'sting-like-a-bee',
			'symbols': [
				Card.SYMBOLS['type']['talent'],
				Card.SYMBOLS['action']['damage'],
				Card.SYMBOLS['talent']['other']
			]
		}

		return card_info

	@staticmethod
	def check_draw_condition(player):
		if get_talent(player, 'temperance'):
			return False
		
		if get_talent(player, 'float_like_a_butterfly'):
			return True
		
		return False
		
	def __init__(self, scene, player):
		super().__init__(scene, player)

		self.talent_info['crit_chance_increase'] = .35
		self.talent_info['buff_signature'] = 'sting_like_a_bee'

	def update(self, scene, dt):
		current_buff = get_buff(self.player, self.talent_info['buff_signature'])
		speed_boost = abs(self.player.velocity[0]) > self.player.movement_info['max_movespeed']
		
		if not speed_boost and current_buff:
			current_buff.end()

		if speed_boost and not current_buff:
			buff = Buff(self.player, self.talent_info['buff_signature'], 'crit_strike_chance', self.talent_info['crit_chance_increase'], None)
			self.player.buffs.append(buff)

class Marksman(Talent):
	TALENT_ID = 'marksman'
	TALENT_CALLS = ['on_@primary']

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

		self.talent_info['min_distance'] = 500
		self.talent_info['per_damage_distance_ratio'] = [.05, 100]
		self.talent_info['max_distance'] = False

	def call(self, call, scene, info):
		distance = get_distance(self.player.center_position, info.destination)
		if distance < self.talent_info['min_distance']:
			return
		
		super().call(call, scene, info)

		distance = round(distance / self.talent_info['per_damage_distance_ratio'][1])
		info.ability_info['damage'] *= round(distance * self.talent_info['per_damage_distance_ratio'][0], 2) + 1

class Temperance(Talent):
	TALENT_ID = 'temperance'

	DESCRIPTION = {
		'name': 'Temperance',
		'description': 'You can no longer critical strike but gain a permanent damage increase.'
	}

	def __init__(self, scene, player):
		super().__init__(scene, player)

		self.talent_info['damage_multiplier'] = 0.25

		damage_buff = Buff(self.player, 'temperance', 'damage_multiplier', self.talent_info['damage_multiplier'], None)
		crit_chance_debuff = Debuff(self.player, 'temperance', 'crit_strike_chance', -100, None)

		self.player.buffs.append(damage_buff)
		self.player.debuffs.append(crit_chance_debuff)
		
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
	
	@staticmethod
	def check_draw_condition(player):
		return True

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
	
	@staticmethod
	def check_draw_condition(player):
		return True

	def __init__(self, scene, player):
		super().__init__(scene, player)

		self.talent_info['stats'] = {
			'max_health': 20,
			'base_damage': 5,
			'crit_strike_chance': .15,
			'crit_strike_multiplier': .5,
			'max_movespeed': 3
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

		stat = random.choice(list(self.talent_info['stats'].keys()))
		while stat == self.talent_info['current_stat']:
			stat = random.choice(list(self.talent_info['stats'].keys()))

		health_proportion = self.player.get_stat('health') / self.player.get_stat('max_health')

		current_buff = get_buff(self.player, self.talent_info['buff_signature'])
		if current_buff:
			current_buff.end()

		buff = Buff(self.player, self.talent_info['buff_signature'], stat, self.talent_info['stats'][stat], None)
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
		'description': 'Taking damage will apply a resistance towards that type of damage for a short time.'
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

		self.talent_info['mitigation_amount'] = .2
		self.talent_info['mitigation_time'] = 60
	
	def call(self, call, scene, info):
		super().call(call, scene, info)

		self.player.combat_info['mitigations'][info['type']][self.TALENT_ID] = [self.talent_info['mitigation_amount'], self.talent_info['mitigation_time']]

class GuardianAngel(Talent):
	TALENT_ID = 'guardian_angel'
	TALENT_CALLS = ['on_player_death']

	DESCRIPTION = {
		'name': 'Guardian Angel',
		'description': 'Upon taking fatal damage you heal a portion of your max health. Can only occur 3 times.'
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

		self.talent_info['charges'] = 3
	
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
	TALENT_CALLS = ['on_player_attack']

	DESCRIPTION = {
		'name': 'Chain Reaction',
		'description': 'Your attacks now chain up to 3 times around your target.'
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
		self.talent_info['damage_percentage'] = .8
	
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
			register_damage(
				scene,
				self.player,
				enemy,
				{'type': info['type'], 'amount': info['amount'] * self.talent_info['damage_percentage']}
			)

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

class Reprisal(Talent):
	TALENT_ID = 'reprisal'
	TALENT_CALLS = ['on_player_damaged']

	DESCRIPTION = {
		'name': 'Reprisal',
		'description': 'Taking damage summons a familiar that will temporarily attack nearby enemies.'
	}

	@staticmethod
	def fetch():
		card_info = {
			'type': 'talent',
			
			'icon': 'reprisal',
			'symbols': [				
				Card.SYMBOLS['type']['talent'],
				Card.SYMBOLS['action']['damage'],
				Card.SYMBOLS['talent']['hurt/death']
			]
		}

		return card_info
	
	def __init__(self, scene, player):
		super().__init__(scene, player)

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

class ChaosTheory(Talent):
	TALENT_ID = 'chaos_theory'
	TALENT_CALLS = []

	DESCRIPTION = {
		'name': 'Chaos Theory',
		'description': '???'
	}

	@staticmethod
	def fetch():
		card_info = {
			'type': 'talent',
			
			'icon': 'chaos-theory',
			'symbols': [				
				Card.SYMBOLS['type']['talent'],
				Card.SYMBOLS['action']['other'],
				Card.SYMBOLS['talent']['other']
			]
		}

		return card_info
	
	def __init__(self, scene, player):
		super().__init__(scene, player)