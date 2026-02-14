import pygame

from circleshape import CircleShape
from shot import Shot
from constants import PLAYER_RADIUS, PLAYER_TURN_SPEED, PLAYER_SPEED, LINE_WIDTH, PLAYER_SHOOT_SPEED


class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0

    def triangle(self):
        # Calculate triangle vertices for the player ship
        # Forward vector points in direction of rotation
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        # Right vector is perpendicular, scaled down for ship width
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        # Front point of ship
        a = self.position + forward * self.radius
        # Back left point
        b = self.position - forward * self.radius - right
        # Back right point
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw(self, screen):
        pygame.draw.polygon(screen, "white", self.triangle(), LINE_WIDTH)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rotation += PLAYER_TURN_SPEED * dt  # Turn left (counterclockwise)
        if keys[pygame.K_d]:
            self.rotation -= PLAYER_TURN_SPEED * dt  # Turn right (clockwise)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_SPACE]:
            self.shoot()

    def move(self, dt):
        # Create unit vector pointing up (0, 1)
        unit_vector = pygame.Vector2(0, 1)
        # Rotate to match player's current facing direction
        rotated_vector = unit_vector.rotate(self.rotation)
        # Scale by speed and delta time for frame-independent movement
        rotated_with_speed_vector = rotated_vector * PLAYER_SPEED * dt
        self.position += rotated_with_speed_vector

    def shoot(self):
        """Creates a new Shot at the current position of the player.

        Sets the shot's .velocity attribute:
        Start with a pygame.Vector2 of (0, 1).
        .rotate() the vector in the direction the player is facing.
        Scale it up (multiply by PLAYER_SHOOT_SPEED) to make it move faster.
        """
        s = Shot(self.position.x, self.position.y)
        # Create unit vector pointing up (0, 1)
        # Rotate to match player's current facing direction
        unit_vector = pygame.Vector2(0, 1)
        rotated_vector = unit_vector.rotate(self.rotation)
        s.velocity = rotated_vector * PLAYER_SHOOT_SPEED

