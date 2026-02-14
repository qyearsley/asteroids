import pygame

# Base class for game objects
class CircleShape(pygame.sprite.Sprite):
    def __init__(self, x, y, radius):
        # we will be using this later
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

    def collides_with(self, other):
        """Check whether circle overlaps."""
        return self.position.distance_to(other.position) < self.radius + other.radius
