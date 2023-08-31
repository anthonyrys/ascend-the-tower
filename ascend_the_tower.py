def main(screen, clock, scene_handler):
    quit = False

    while not quit:
        screen.fill(SCREEN_COLOR)

        quit = scene_handler.update()
        pygame.display.flip()

        clock.tick(FRAME_RATE)

if __name__ == '__main__':
    from scripts import (
        TITLE, VERSION,
        FRAME_RATE,
        SCREEN_DIMENSIONS,
        SCREEN_COLOR
    )
    
    from scripts.scene_handler import SceneHandler
    
    from scripts.tools.sfx_manager import Sfx
    from scripts.tools.fonts import Fonts
    from scripts.tools.inputs import Inputs

    import pygame
    import sys
    
    pygame.init()

    pygame.display.set_caption(f'{TITLE} [{VERSION}]')
    pygame.mouse.set_visible(False)

    screen = pygame.display.set_mode(SCREEN_DIMENSIONS)
    clock = pygame.time.Clock()
    
    Sfx.init()

    Fonts.init()
    Inputs.init()

    main(screen, clock, SceneHandler(screen, clock))
    
    pygame.quit()
    sys.exit()
