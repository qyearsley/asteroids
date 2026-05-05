import pygame

from constants import SCREEN_WIDTH, SCREEN_HEIGHT


# Base class for game objects
class CircleShape(pygame.sprite.Sprite):
    def __init__(self, x, y, radius):
        # Auto-register with sprite groups assigned to the class's `containers` attribute.
        # This is how pygame sprites can add themselves to groups on creation.
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def draw(self, screen):
        # Subclasses must implement this method
        raise NotImplementedError("Subclass must implement draw()")

    def update(self, dt):
        # Subclasses must implement this method
        raise NotImplementedError("Subclass must implement update()")

    def wrap_position(self):
        """Wrap position around screen edges so objects reappear on the opposite side."""
        if self.position.x < 0:
            self.position.x += SCREEN_WIDTH
        elif self.position.x > SCREEN_WIDTH:
            self.position.x -= SCREEN_WIDTH
        if self.position.y < 0:
            self.position.y += SCREEN_HEIGHT
        elif self.position.y > SCREEN_HEIGHT:
            self.position.y -= SCREEN_HEIGHT

    def collides_with(self, other):
        """Check whether circle overlaps."""
        return self.position.distance_to(other.position) < self.radius + other.radius
