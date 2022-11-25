def main(screen, clock, scene_handler):
    quit = False

    while not quit:
        screen.fill(SCREEN_COLOR)

        quit = scene_handler.update()
        pygame.display.flip()

        clock.tick(FRAME_RATE)

if __name__ == '__main__':
    from src.constants import (
        TITLE,
        FRAME_RATE,
        SCREEN_DIMENSIONS,
        SCREEN_COLOR
    )
    from src.engine import Fonts

    from src.scenes.scene_handler import SceneHandler

    import pygame
    import sys
    
    pygame.init()

    Fonts.init()

    pygame.display.set_caption(TITLE)
    pygame.mouse.set_visible(False)

    screen = pygame.display.set_mode(SCREEN_DIMENSIONS)
    main(screen, pygame.time.Clock(), SceneHandler(screen))
    
    pygame.quit()
    sys.exit()
