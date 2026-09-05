import pygame

from circleshape import CircleShape
from constants import (
    PARTICLE_COUNT,
    PARTICLE_LIFETIME,
    PARTICLE_RADIUS,
    PARTICLE_SPEED_MAX,
    PARTICLE_SPEED_MIN,
)
import rng


class Particle(CircleShape):
    """A short-lived dot that flies outward from an explosion point."""

    def __init__(self, x, y):
        super().__init__(x, y, PARTICLE_RADIUS)
        self.lifetime = PARTICLE_LIFETIME
        # Pick a random direction (0-360 degrees) and random speed.
        angle = rng.effects.uniform(0, 360)
        speed = rng.effects.uniform(PARTICLE_SPEED_MIN, PARTICLE_SPEED_MAX)
        self.velocity = pygame.Vector2(0, 1).rotate(angle) * speed

    def draw(self, screen):
        # Fade from white to black as the lifetime runs out. Not transparency:
        # this is a greyscale ramp on an opaque circle, which reads as a fade
        # only because the background is black. Alpha would need a per-surface
        # blit; the ramp costs nothing and looks the same here.
        level = int(255 * (self.lifetime / PARTICLE_LIFETIME))
        pygame.draw.circle(screen, (level, level, level), self.position, self.radius)

    def update(self, dt):
        self.position += self.velocity * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()


def spawn_explosion(x, y):
    """Create a burst of particles at the given position."""
    for _ in range(PARTICLE_COUNT):
        Particle(x, y)
