import pygame

import constants
import logger
import player


def main():
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
    print(f"Screen width: {constants.SCREEN_WIDTH}")
    print(f"Screen height: {constants.SCREEN_HEIGHT}")
    clock = pygame.time.Clock()
    dt = 0
    pl = player.Player(constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2)
    while True:
        logger.log_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        screen.fill("black")
        pl.update(dt)
        pl.draw(screen)
        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()
