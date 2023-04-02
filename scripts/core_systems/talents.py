from scripts.constants import HEAL_COLOR
from scripts.engine import get_distance

from scripts.core_systems.combat_handler import register_heal

from scripts.entities.particle_fx import Image, Circle

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
		'description': 'Gain additional critical strike chance when you are fast.'
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
		self.talent_info['crit_chance_given'] = False

	def update(self, scene, dt):
		if abs(self.player.velocity[0]) <= self.player.movement_info['max_movespeed']:
			if self.talent_info['crit_chance_given']:
				self.talent_info['crit_chance_given'] = False
				self.player.combat_info['crit_strike_chance'] -= self.talent_info['crit_chance_increase']

		if abs(self.player.velocity[0]) > self.player.movement_info['max_movespeed']:
			if not self.talent_info['crit_chance_given']:
				self.talent_info['crit_chance_given'] = True
				self.player.combat_info['crit_strike_chance'] += self.talent_info['crit_chance_increase']

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
			'health': 20,
			'base_damage': 5,
			'crit_strike_chance': .15,
			'crit_strike_multiplier': .5,
			'max_movespeed': 3
		}

		self.talent_info['names'] = {
			'health': 'health',
			'base_damage': 'damage',
			'crit_strike_chance': 'crit chance',
			'crit_strike_multiplier': 'crit multiplier',
			'max_movespeed': 'speed'
		}

		self.talent_info['current_stat'] = None

		self.talent_info['cooldown_timer'] = 300

	def update(self, scene, dt):
		super().update(scene, dt)

		if self.talent_info['cooldown'] > 0:
			return
		
		self.talent_info['cooldown'] = self.talent_info['cooldown_timer']

		stat = random.choice(list(self.talent_info['stats'].keys()))
		while stat == self.talent_info['current_stat']:
			stat = random.choice(list(self.talent_info['stats'].keys()))

		if self.talent_info['current_stat'] is not None:
			if self.talent_info['current_stat'] == 'max_movespeed':
				self.player.movement_info['max_movespeed'] -= self.talent_info['stats']['max_movespeed']

			elif self.talent_info['current_stat'] == 'health':
				self.player.combat_info['max_health'] -= self.talent_info['stats']['health']

			else:
				self.player.combat_info[self.talent_info['current_stat']] -= self.talent_info['stats'][self.talent_info['current_stat']]

		if stat == 'max_movespeed':
			self.player.movement_info[stat] += self.talent_info['stats']['max_movespeed']

		elif stat == 'health':
			self.player.combat_info['max_health'] += self.talent_info['stats']['health']
			self.player.combat_info['health'] += self.talent_info['stats']['health']

		else:
			self.player.combat_info[stat] += self.talent_info['stats'][stat]

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
			
		self.talent_info['current_stat'] = stat
	
class Recuperation(Talent):
	TALENT_ID = 'recuperation'
	TALENT_CALLS = ['on_damaged']

	DESCRIPTION = {
		'name': 'Recuperation',
		'description': 'Gain an orb every couple seconds you dont take damage. Once damaged, your orbs will heal you.'
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

		self.talent_info['cooldown_timer'] = 80

		self.talent_info['heal_amount'] = 3

		self.talent_info['orb_info'] = {
			'count': 0,
			'max_count': 3,

			'radius': 30,
			'angle_speed': 3,

			'imgs': []
		}

		self.talent_info['img_info'] = {
			'size': 5,
			'color': (125, 255, 125),
			'copy': None
		}

		img_copy = pygame.Surface((self.talent_info['img_info']['size'] * 2, self.talent_info['img_info']['size'] * 2)).convert_alpha()
		img_copy.fill((0, 0, 0, 0))
		pygame.draw.circle(img_copy, self.talent_info['img_info']['color'], (img_copy.get_width() * .5, img_copy.get_height() * .5), self.talent_info['img_info']['size'])

		self.talent_info['img_info']['copy'] = img_copy

	def update(self, scene, dt):
		super().update(scene, dt)
		
		for img in self.talent_info['orb_info']['imgs']:
			img['angle'] += self.talent_info['orb_info']['angle_speed'] * dt

			if self.player.ability_override:
				continue

			a = (img['angle'] - 90) * math.pi / 180
			x = self.talent_info['orb_info']['radius'] * math.cos(a)
			y = self.talent_info['orb_info']['radius'] * math.sin(a)

			pos = [
				self.player.center_position[0] + x,
				self.player.center_position[1] + y
			]

			img['pos'] = pos

			scene.entity_surface.blit(img['img'], img['img'].get_rect(center=pos))

			for i in range(7):
				size = (self.talent_info['img_info']['size'] * 2) - i
				delay = pygame.transform.scale(img['img'], (size, size))

				ab = ((img['angle'] - self.talent_info['orb_info']['angle_speed'] * (i + 2)) - 90) * math.pi / 180
				xb = self.talent_info['orb_info']['radius'] * math.cos(ab)
				yb = self.talent_info['orb_info']['radius'] * math.sin(ab)

				posb = [
					self.player.center_position[0] + xb,
					self.player.center_position[1] + yb
				]

				scene.entity_surface.blit(delay, delay.get_rect(center=posb))

		if self.talent_info['cooldown'] > 0:
			return
		
		self.talent_info['cooldown'] = self.talent_info['cooldown_timer']

		if self.talent_info['orb_info']['count'] >= self.talent_info['orb_info']['max_count']:
			return
		
		self.talent_info['orb_info']['count'] += 1
		self.talent_info['orb_info']['imgs'].append({'angle': 0, 'pos': (0, 0), 'img': self.talent_info['img_info']['copy'].copy()})
		
	def call(self, call, scene, info):
		super().call(call, scene, info)
		self.talent_info['cooldown'] = self.talent_info['cooldown_timer']

		if self.talent_info['orb_info']['count'] > 0:
			register_heal(scene, self.player, {'amount': self.talent_info['heal_amount'] * self.talent_info['orb_info']['count'], 'type': 'status'})

		self.talent_info['orb_info']['count'] = 0

		for img in self.talent_info['orb_info']['imgs']:
			particles = []
			for _ in range(3):
				circ = Circle(img['pos'], self.talent_info['img_info']['color'], 5, 0)
				circ.set_goal(45, position=(img['pos'][0] + random.randint(-100, 100), img['pos'][1] + random.randint(100, 200)), radius=1)
				circ.set_gravity(-5)
				
				particles.append(circ)

			scene.add_sprites(particles)

		self.talent_info['orb_info']['imgs'] = []

class Holdfast(Talent):
	TALENT_ID = 'holdfast'
	TALENT_CALLS = ['on_damaged']

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
		self.player.combat_info['mitigations'][info['type']][self.TALENT_ID] = [self.talent_info['mitigation_amount'], self.talent_info['mitigation_time']]

class GuardianAngel(Talent):
	TALENT_ID = 'guardian_angel'

	DESCRIPTION = {
		'name': 'Guardian Angel',
		'description': 'Upon taking fatal damage you heal a portion of your max health (once per wave).'
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