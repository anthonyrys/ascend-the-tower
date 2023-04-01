from scripts.engine import get_distance

from scripts.core_systems.combat_handler import register_damage, register_heal

from scripts.ui.card import Card

import inspect
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
	TALENT_ID = None
	TALENT_CALLS = []

	DESCRIPTION = {
		'name': None,
		'description': None
	}

	def __init__(self, player):
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

	def __init__(self, player):
		super().__init__(player)

		self.talent_info['heal_amount'] = 0.2

	def call(self, call, scene, info):
		super().call(call, scene, info)

		register_heal(scene, self.player, {'type': 'status', 'amount': info['amount'] * self.talent_info['heal_amount']})

class ComboStar(Talent):
	TALENT_ID = 'combo_star'
	TALENT_CALLS = ['on_player_attack']

	DESCRIPTION = {
		'name': 'Combo Star',
		'description': 'Deal additional damage when chaining|your attacks in quick succession.'
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

	def __init__(self, player):
		super().__init__(player)

		self.talent_info['multiplier'] = 0
		self.talent_info['per_multiplier'] = .2
		self.talent_info['multiplier_cap'] = 1.0

		self.talent_info['time'] = 0
		self.talent_info['decay_time'] = 45

	def call(self, call, scene, info):
		super().call(call, scene, info)

		self.talent_info['time'] = self.talent_info['decay_time']
		if self.talent_info['multiplier'] < self.talent_info['multiplier_cap']:
			self.player.combat_info['damage_multiplier'] = round(self.player.combat_info['damage_multiplier'] + self.talent_info['per_multiplier'], 2)
			self.talent_info['multiplier'] = round(self.talent_info['multiplier'] + self.talent_info['per_multiplier'], 2)

	def update(self, scene, dt):
		if self.talent_info['time'] <= 0 and self.talent_info['multiplier'] != 0:
			self.player.combat_info['damage_multiplier'] = round(self.player.combat_info['damage_multiplier'] - self.talent_info['multiplier'], 2)
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

		self.player.movement_info['friction'] = .5
		self.player.movement_info['friction_frames'] = 30

class StingLikeABee(Talent):
	TALENT_ID = 'sting_like_a_bee'

	DESCRIPTION = {
		'name': 'Sting Like A Bee',
		'description': 'Increased critical strike chance when|you are fast.'
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
		
	def __init__(self, player):
		super().__init__(player)

		self.talent_info['crit_chance_increase'] = .2
		self.talent_info['crit_chance_given'] = False

	def update(self, scene, dt):
		if abs(self.player.velocity[0]) <= self.player.movement_info['max_movespeed']:
			if self.talent_info['crit_chance_given']:
				self.talent_info['crit_chance_given'] = False
				self.player.combat_info['crit_strike_chance'] -= .2

		if abs(self.player.velocity[0]) > self.player.movement_info['max_movespeed']:
			if not self.talent_info['crit_chance_given']:
				self.talent_info['crit_chance_given'] = True
				self.player.combat_info['crit_strike_chance'] += .2

class Marksman(Talent):
	TALENT_ID = 'marksman'
	TALENT_CALLS = ['on_@primary']

	DESCRIPTION = {
		'name': 'Marksman',
		'description': 'Your primary attack deals more|damage the farther your target is.'
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

	def __init__(self, player):
		super().__init__(player)

		self.talent_info['min_distance'] = 500
		self.talent_info['per_damage_distance_ratio'] = [.05, 50]
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
		'description': 'You can no longer critical strike|but gain a permanent 25 percent|damage increase.'
	}

	def __init__(self, player):
		super().__init__(player)

		self.talent_info['damage_multiplier'] = 0.25

		self.player.combat_info['damage_multiplier'] = round(self.player.combat_info['damage_multiplier'] + self.talent_info['damage_multiplier'], 2)
		self.player.combat_info['crit_strike_chance'] = -100
		
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