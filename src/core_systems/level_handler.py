import math

class Level:
    MAX_LEVEL = 50

    BASE_PLAYER_EXPERIENCE_CAP = 100
    PLAYER_EXPERIENCE_CURVE = 1.85

    BASE_ENEMY_EXPERIENCE_AMOUNT = 30
    ENEMY_EXPERIENCE_CURVE = .95

    STATS_PER_POINTS = {
        'speed': [.25, 1],
        'health': 10,
        'damage': 5,
        'crit_strike_chance': .02,
        'crit_strike_multiplier': .05,
    }

    @staticmethod
    def level_up(scene):
        player = scene.player

        player.level_info['level'] += 1
        player.level_info['experience'] = 0
        player.level_info['max_experience'] = Level.BASE_PLAYER_EXPERIENCE_CAP + round(math.pow(player.level_info['level'], Level.PLAYER_EXPERIENCE_CURVE))

    @staticmethod
    def calculate_experience(level, multiplier=1):
        return round((Level.BASE_ENEMY_EXPERIENCE_AMOUNT + math.pow(level, Level.ENEMY_EXPERIENCE_CURVE)) * multiplier)

    @staticmethod
    def register_experience(scene, amount):
        player = scene.player

        leveled = False
        if player.level_info['experience'] + amount >= player.level_info['max_experience']:
            amount = abs((player.level_info['experience'] + amount) - player.level_info['max_experience'])
            Level.level_up(scene)
            player.on_level_up(scene)

            leveled = True
        
        player.level_info['experience'] += amount
        player.on_experience_gained(scene)

        return leveled

