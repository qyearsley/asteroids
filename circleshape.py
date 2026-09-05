import pygame

from constants import SCREEN_HEIGHT, SCREEN_WIDTH


class CircleShape(pygame.sprite.Sprite):
    """Base class for everything on screen: a position, a velocity, a radius.

    Collision is circle-to-circle throughout the game, which is why the radius
    lives here rather than on each subclass. Subclasses supply `draw` and
    `update`; this class supplies the two things every one of them needs, screen
    wrapping and overlap.
    """

    def __init__(self, x, y, radius):
        # Auto-register with sprite groups assigned to the class's `containers`
        # attribute, which is how a sprite joins a group simply by existing.
        # Guarded, because a test may build one with no groups attached.
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def draw(self, screen):
        raise NotImplementedError("Subclass must implement draw()")

    def update(self, dt):
        raise NotImplementedError("Subclass must implement update()")

    def wrap_position(self):
        """Bring the object back on screen from the opposite edge.

        Written as a modulo rather than a single step, so an object that has
        somehow travelled more than one screen width in a frame arrives
        somewhere sensible instead of still being off the edge. The `elif`
        version this replaces moved it by exactly one screen and no more.
        """
        self.position.x %= SCREEN_WIDTH
        self.position.y %= SCREEN_HEIGHT

    def collides_with(self, other):
        """Whether this circle overlaps another. Touching exactly does not count."""
        return self.position.distance_to(other.position) < self.radius + other.radius
