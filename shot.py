import pygame

from circleshape import CircleShape
from constants import SHOT_LIFETIME_SECONDS, SHOT_RADIUS


class Shot(CircleShape):
    """A bullet. Wraps at the screen edge, and disappears after a fixed time.

    The lifetime is what stops a shot being permanent. Without it a bullet
    circled the screen until it hit something, so a run accumulated one more
    sprite every 0.3 seconds for as long as it lasted, and holding the fire
    button cleared the field by attrition rather than by aim.
    """

    def __init__(self, x, y):
        super().__init__(x, y, SHOT_RADIUS)
        self.life_left = SHOT_LIFETIME_SECONDS

    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, self.radius)

    def update(self, dt):
        self.life_left -= dt
        if self.life_left <= 0:
            self.kill()
            return
        self.position += self.velocity * dt
        self.wrap_position()
