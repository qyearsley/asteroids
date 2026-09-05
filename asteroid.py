import pygame

from circleshape import CircleShape
from constants import (
    ASTEROID_MIN_RADIUS,
    ASTEROID_SPLIT_ANGLE_MAX,
    ASTEROID_SPLIT_ANGLE_MIN,
    ASTEROID_SPLIT_SPEED_MULTIPLIER,
)
import logger
import rng


class Asteroid(CircleShape):
    """A drifting rock that wraps at the screen edge and breaks in two when shot."""

    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, self.radius)

    def update(self, dt):
        self.position += self.velocity * dt
        self.wrap_position()

    def split(self):
        """Break this asteroid up, or simply remove it if it is already small.

        Always kills this asteroid first, whichever happens next: a shot that
        lands is a shot that lands. Only one larger than the minimum radius
        leaves children -- two of them, deflected symmetrically off the parent's
        heading and slightly faster, which is what turns one big slow target
        into a spreading problem.

        The two velocities are worked out before either child exists, because a
        child registers itself with the sprite groups the moment it is built and
        the deflection has to be symmetric about the parent's original heading.
        """
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        logger.log_event("asteroid_split")
        angle = rng.effects.uniform(ASTEROID_SPLIT_ANGLE_MIN, ASTEROID_SPLIT_ANGLE_MAX)
        new_velocity1 = self.velocity.rotate(angle) * ASTEROID_SPLIT_SPEED_MULTIPLIER
        new_velocity2 = self.velocity.rotate(-angle) * ASTEROID_SPLIT_SPEED_MULTIPLIER
        new_radius = self.radius - ASTEROID_MIN_RADIUS
        a1 = Asteroid(self.position.x, self.position.y, new_radius)
        a2 = Asteroid(self.position.x, self.position.y, new_radius)
        a1.velocity = new_velocity1
        a2.velocity = new_velocity2
