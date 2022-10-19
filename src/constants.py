import pygame

TITLE = 'untitled'
FRAME_RATE = 30

SCREEN_DIMENSIONS = pygame.Vector2(1280, 720)
SCREEN_COLOR = pygame.Color(44, 44, 44)

BG_COLOR = pygame.Color(40, 40, 40)

GRAVITY = 2
MAX_GRAVITY = 30


COLORS = ['red', 'blue', 'yellow']
COLOR_VALUES = {
    COLORS[0]: pygame.Color(245, 84, 66),
    COLORS[1]: pygame.Color(66, 84, 245),
    COLORS[2]: pygame.Color(255, 255, 84)
}

COLOR_VALUES_PRIMARY = {
    COLORS[0]: pygame.Color(255, 94, 76),
    COLORS[1]: pygame.Color(76, 94, 255),
    COLORS[2]: pygame.Color(255, 255, 124)
}

COLOR_VALUES_SECONDARY = {
    COLORS[0]: pygame.Color(255, 114, 96),
    COLORS[1]: pygame.Color(96, 114, 255),
    COLORS[2]: pygame.Color(255, 255, 164)
}
