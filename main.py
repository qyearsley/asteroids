#!/usr/bin/env python3
import logger
import sys

import pygame

import asteroid
import asteroidfield
import constants
import player
import shot


def main():
    """Main entry point and game loop."""
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")

    screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
    print(f"Screen width: {constants.SCREEN_WIDTH}")
    print(f"Screen height: {constants.SCREEN_HEIGHT}")

    # Clock controls frame rate.
    clock = pygame.time.Clock()

    # Create sprite groups for game object management
    updatable = pygame.sprite.Group()  # Objects that need update() called
    drawable = pygame.sprite.Group()  # Objects that need draw() called
    asteroids = pygame.sprite.Group()  # Asteroids for collision detection
    shots = pygame.sprite.Group()

    # Assign sprite groups as class-level containers
    # Objects will auto-add themselves to these groups on instantiation
    asteroid.Asteroid.containers = (asteroids, updatable, drawable)
    player.Player.containers = (updatable, drawable)
    shot.Shot.containers = (shots, updatable, drawable)

    p = player.Player(constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2)
    asteroidfield.AsteroidField.containers = (updatable,)
    asteroidfield.AsteroidField()

    dt = 0  # Delta time in seconds
    while True:
        logger.log_state()

        # Handle quit events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        # Clear screen.
        screen.fill("black")

        # Update all game objects.
        for x in updatable:
            x.update(dt)

        # Check for collisions between player and asteroids.
        for x in asteroids:
            if x.collides_with(p):
                logger.log_event("player_hit")
                print("Game over!")
                sys.exit()
            for s in shots:
                if x.collides_with(s):
                    logger.log_event("asteroid_shot")
                    x.kill()
                    s.kill()

        # Draw all game objects.
        for x in drawable:
            x.draw(screen)

        # Update display and calculate delta time.
        pygame.display.flip()
        dt = clock.tick(60) / 1000  # Limit to 60 FPS, convert ms to seconds


if __name__ == "__main__":
    main()
