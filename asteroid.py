import pygame
import random
from logger import log_event

from constants import ASTEROID_MIN_RADIUS
from circleshape import CircleShape


class Asteroid(CircleShape):
    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, self.radius)

    def update(self, dt):
        self.position += self.velocity * dt

    def split(self):
        """Split a asteroid into more asteroids if it's not a small asteroid."""
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        log_event("asteroid_split")
        # 1. Calculate all necessary values first
        angle = random.uniform(20, 50)
        new_velocity1 = self.velocity.rotate(angle) * 1.2
        new_velocity2 = self.velocity.rotate(-angle) * 1.2
        new_radius = self.radius - ASTEROID_MIN_RADIUS
        # 2. Create the new objects
        a1 = Asteroid(self.position.x, self.position.y, new_radius)
        a2 = Asteroid(self.position.x, self.position.y, new_radius)
        # 3. Assign the pre-calculated velocities
        a1.velocity = new_velocity1
        a2.velocity = new_velocity2
