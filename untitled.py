def main(screen, clock, scene_handler):
    quit = False

    while not quit:
        screen.fill(SCREEN_COLOR)

        quit = scene_handler.update()
        pygame.display.flip()

        pygame.display.set_caption(f'{TITLE} | fps: {round(clock.get_fps(), 1)}')
        clock.tick(FRAME_RATE)

if __name__ == '__main__':
    from scripts.constants import (
        TITLE,
        FRAME_RATE,
        SCREEN_DIMENSIONS,
        SCREEN_COLOR
    )
    from scripts.engine import (
        Fonts,
        Inputs
    )

    from scripts.scenes.scene_handler import SceneHandler

    import pygame
    import sys
    
    pygame.init()

    pygame.display.set_caption(TITLE)
    pygame.mouse.set_visible(False)

    screen = pygame.display.set_mode(SCREEN_DIMENSIONS)
    clock = pygame.time.Clock()

    Fonts.init()
    Inputs.init()

    main(screen, clock, SceneHandler(screen, clock))
    
    pygame.quit()
    sys.exit()
