import pygame

from circleshape import CircleShape
from constants import (
    LINE_WIDTH,
    PLAYER_INVINCIBILITY_SECONDS,
    PLAYER_RADIUS,
    PLAYER_SHOOT_COOLDOWN_SECONDS,
    PLAYER_SHOOT_SPEED,
    PLAYER_SPEED,
    PLAYER_TURN_SPEED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from shot import Shot


class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shot_cooldown_timer = 0
        self.invincibility_timer = 0

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
        # Blink rapidly while invincible to signal protection to the player.
        # Multiplying by 10 and checking % 2 gives 5 blinks per second.
        if self.invincibility_timer > 0 and int(self.invincibility_timer * 10) % 2 == 0:
            return
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
        self.shot_cooldown_timer -= dt
        self.invincibility_timer -= dt
        self.wrap_position()

    def move(self, dt):
        # Create unit vector pointing up (0, 1)
        unit_vector = pygame.Vector2(0, 1)
        # Rotate to match player's current facing direction
        rotated_vector = unit_vector.rotate(self.rotation)
        # Scale by speed and delta time for frame-independent movement
        rotated_with_speed_vector = rotated_vector * PLAYER_SPEED * dt
        self.position += rotated_with_speed_vector

    def respawn(self):
        """Reset position to center and grant invincibility."""
        self.position = pygame.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.velocity = pygame.Vector2(0, 0)
        self.rotation = 0
        self.invincibility_timer = PLAYER_INVINCIBILITY_SECONDS

    def shoot(self):
        """Creates a new Shot at the current position of the player."""
        if self.shot_cooldown_timer > 0:
            return
        self.shot_cooldown_timer = PLAYER_SHOOT_COOLDOWN_SECONDS
        s = Shot(self.position.x, self.position.y)
        # Create unit vector pointing up (0, 1)
        # Rotate to match player's current facing direction
        unit_vector = pygame.Vector2(0, 1)
        rotated_vector = unit_vector.rotate(self.rotation)
        s.velocity = rotated_vector * PLAYER_SHOOT_SPEED
