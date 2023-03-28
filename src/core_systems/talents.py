from src.engine import SpriteMethods

from src.core_systems.combat_handler import Combat

import inspect
import sys

class Talent:
	TALENT_ID = None
	TALENT_CALLS = []

	def __init__(self, player):
		self.player = player
		self.overrides = False
		
		self.talent_info = {
            'cooldown_timer': 0,
            'cooldown': 0
		}
		
	@staticmethod
	def get_all_talents():
		talent_list = []
		for talent in inspect.getmembers(sys.modules[__name__], inspect.isclass):
			if not issubclass(talent[1], Talent) or talent[1].TALENT_ID is None:
				continue
			
			talent_list.append(talent[1])
			
		return talent_list
	
	@staticmethod
	def get_talent(player, talent_id):
		for talent in player.talents:
			if talent.TALENT_ID != talent_id:
				continue

			return talent
	
	@staticmethod
	def call_talents(scene, player, calls):
		for call, info in calls.items():
			for talent in player.talents:
				if call not in talent.TALENT_CALLS:
					continue
				
				talent.call(call, scene, info)

	@staticmethod
	def reset_talents(player):
		for talent in player.talents:
			talent.reset()

	@staticmethod
	def check_draw_condition(player):
		return True

	def call(self, call, scene, info=None):
		print(f'{self.TALENT_ID}::call({call})')

	def reset(self):
		...

	def update(self, scene, dt):
		if self.talent_info['cooldown'] > 0:
			self.talent_info['cooldown'] -= 1 * dt

class Vamprism(Talent):
	TALENT_ID = 'vamprism'
	TALENT_CALLS = ['on_player_attack']

	TALENT_DESCRIPTION = {
		'name': 'Vamprism',
		'description': 'Heal a portion of the damage you deal.'
	}

	def __init__(self, player):
		super().__init__(player)

		self.talent_info['heal_amount'] = 0.2

	def call(self, call, scene, info):
		super().call(call, scene, info)

		Combat.register_heal(scene, self.player, {'type': 'status', 'amount': info['amount'] * self.talent_info['heal_amount']})

class ComboStar(Talent):
	TALENT_ID = 'combo_star'
	TALENT_CALLS = ['on_player_attack']

	TALENT_DESCRIPTION = {
		'name': 'Combo Star',
		'description': 'Deal additional damage when chaining your attacks in quick succession.'
	}

	def __init__(self, player):
		super().__init__(player)

		self.talent_info['multiplier'] = 0
		self.talent_info['per_multiplier'] = .2
		self.talent_info['multiplier_cap'] = 1.0

		self.talent_info['time'] = 0
		self.talent_info['decay_time'] = 45

	def call(self, call, scene, info):
		super().call(call, scene, info)
		
		damage = info['amount'] * self.talent_info['multiplier']
		Combat.register_damage(scene, self.player, info['target'], {'type': info['type'], 'amount': damage})

		self.talent_info['time'] = self.talent_info['decay_time']
		if self.talent_info['multiplier'] < self.talent_info['multiplier_cap']:
			self.talent_info['multiplier'] = round(self.talent_info['multiplier'] + self.talent_info['per_multiplier'], 2)

	def update(self, scene, dt):
		if self.talent_info['time'] <= 0 and self.talent_info['multiplier'] != 0:
			self.talent_info['multiplier'] = 0

		elif self.talent_info['time'] > 0:
			self.talent_info['time'] -= 1 * dt

class FloatLikeAButterfly(Talent):
	TALENT_ID = 'float_like_a_butterfly'
	TALENT_CALLS = ['on_@dash']

	TALENT_DESCRIPTION = {
		'name': 'Float Like A Butterfly',
		'description': 'Increased mobility when dashing.'
	}
	
	def call(self, call, scene, info):
		super().call(call, scene, info)

		self.player.movement_info['friction'] = .5
		self.player.movement_info['friction_frames'] = 30

class StingLikeABee(Talent):
	TALENT_ID = 'sting_like_a_bee'
	TALENT_CALLS = []

	TALENT_DESCRIPTION = {
		'name': 'Sting Like A Bee',
		'description': 'Increased critical strike chance when you are fast.'
	}

	def __init__(self, player):
		super().__init__(player)

		self.talent_info['crit_chance_increase'] = .2
		self.talent_info['crit_chance_given'] = False

	@staticmethod
	def check_draw_condition(player):
		if Talent.get_talent(player, 'float_like_a_butterfly'):
			return True
		
		return False

	def update(self, scene, dt):
		if self.player.velocity[0] <= self.player.movement_info['max_movespeed']:
			if self.talent_info['crit_chance_given']:
				self.talent_info['crit_chance_given'] = False
				self.player.combat_info['crit_strike_chance'] -= .2

		if self.player.velocity[0] > self.player.movement_info['max_movespeed']:
			if not self.talent_info['crit_chance_given']:
				self.talent_info['crit_chance_given'] = True
				self.player.combat_info['crit_strike_chance'] += .2

class Marksman(Talent):
	TALENT_ID = 'marksman'
	TALENT_CALLS = ['on_@primary']

	TALENT_DESCRIPTION = {
		'name': 'Marksman',
		'description': 'Your primary ability deals more damage the farther your target is.'
	}

	def __init__(self, player):
		super().__init__(player)

		self.talent_info['min_distance'] = 500
		self.talent_info['per_damage_distance_ratio'] = [.05, 50]
		self.talent_info['max_distance'] = False

	def call(self, call, scene, info):
		distance = SpriteMethods.get_distance(self.player.center_position, info.destination)
		if distance < self.talent_info['min_distance']:
			return
		
		super().call(call, scene, info)

		distance = round(distance / self.talent_info['per_damage_distance_ratio'][1])
		info.ability_info['damage'] *= round(distance * self.talent_info['per_damage_distance_ratio'][0], 2) + 1
