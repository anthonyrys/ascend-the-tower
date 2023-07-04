import math

class Easings:
    @staticmethod
    def ease_in_sine(abs_prog):
        return 1 - math.cos((abs_prog * math.pi) / 2)

    @staticmethod
    def ease_in_cubic(abs_prog):
        return abs_prog * abs_prog * abs_prog

    @staticmethod
    def ease_in_quint(abs_prog):
        return abs_prog * abs_prog * abs_prog * abs_prog

    @staticmethod
    def ease_in_cir(abs_prog):
        return 1 - math.sqrt(1 - math.pow(abs_prog, 2))

    @staticmethod
    def ease_out_sine(abs_prog):
        return math.sin((abs_prog * math.pi) / 2)

    @staticmethod
    def ease_out_cubic(abs_prog):
        return 1 - math.pow(1 - abs_prog, 3)

    @staticmethod
    def ease_out_quint(abs_prog):
        return 1 - math.pow(1 - abs_prog, 5)

    @staticmethod
    def ease_out_cir(abs_prog):
        return math.sqrt(1 - math.pow(abs_prog - 1, 2))

    @staticmethod
    def custom_position_particle_fx(abs_prog):
        return 1 - pow(1 - abs_prog, 4)
