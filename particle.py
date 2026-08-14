import random

import pygame

from circleshape import CircleShape
from constants import (
    PARTICLE_COUNT,
    PARTICLE_LIFETIME,
    PARTICLE_RADIUS,
    PARTICLE_SPEED_MAX,
    PARTICLE_SPEED_MIN,
)


class Particle(CircleShape):
    """A short-lived dot that flies outward from an explosion point."""

    def __init__(self, x, y):
        super().__init__(x, y, PARTICLE_RADIUS)
        self.lifetime = PARTICLE_LIFETIME
        # Pick a random direction (0-360 degrees) and random speed.
        angle = random.uniform(0, 360)
        speed = random.uniform(PARTICLE_SPEED_MIN, PARTICLE_SPEED_MAX)
        self.velocity = pygame.Vector2(0, 1).rotate(angle) * speed

    def draw(self, screen):
        # Fade from white to transparent over the particle's lifetime.
        # Alpha goes from 255 (fully visible) down to 0 (invisible).
        alpha = int(255 * (self.lifetime / PARTICLE_LIFETIME))
        color = (alpha, alpha, alpha)
        pygame.draw.circle(screen, color, self.position, self.radius)

    def update(self, dt):
        self.position += self.velocity * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()


def spawn_explosion(x, y):
    """Create a burst of particles at the given position."""
    for _ in range(PARTICLE_COUNT):
        Particle(x, y)
