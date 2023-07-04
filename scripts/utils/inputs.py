import pygame

class Inputs:
    KEYBINDS = {
        'left': [pygame.K_a, pygame.K_LEFT],
        'right': [pygame.K_d, pygame.K_RIGHT],
        'down': [pygame.K_s, pygame.K_DOWN],
        'jump': [pygame.K_w, pygame.K_SPACE, pygame.K_UP],

        'ability_1': [pygame.K_1],
        'ability_2': [pygame.K_2],

        'interact': [pygame.K_f]
    }

    MOVEMENT = ['left', 'right', 'down', 'jump']

    pressed = {}

    def init():
        for keybind in Inputs.KEYBINDS.keys():
            Inputs.pressed[keybind] = False

    def get_input_general(input_list):
        for x in input_list:
            if Inputs.pressed[x]:
                return True
            
        return False

    def get_keys_pressed():
        keys = pygame.key.get_pressed()

        for action in Inputs.pressed.keys():
            Inputs.pressed[action] = False

            if not isinstance(Inputs.KEYBINDS[action], list):
                Inputs.pressed[action] = keys[Inputs.KEYBINDS[action]]
                continue

            for val in Inputs.KEYBINDS[action]:
                if not keys[val]:
                    continue

                Inputs.pressed[action] = keys[val]
                break
