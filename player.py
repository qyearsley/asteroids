import pygame

from circleshape import CircleShape
from constants import (
    HULL_WIDTH_RATIO,
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
    """The ship: a triangle that turns, thrusts, and fires.

    Movement is direct translation rather than thrust and drift -- `move` adds
    to `position` and never touches the inherited `velocity`, so the ship stops
    the moment a key comes up. Classic Asteroids coasts; this does not, and
    changing it is a change to how the whole game feels rather than a fix.
    """

    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shot_cooldown_timer = 0
        self.invincibility_timer = 0

    def triangle(self):
        """The ship's three corners, in world coordinates: nose, back left, back right.

        The hull is `HULL_WIDTH_RATIO` times narrower than it is long, which is
        what makes it read as pointing somewhere.
        """
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius * HULL_WIDTH_RATIO
        nose = self.position + forward * self.radius
        back_left = self.position - forward * self.radius - right
        back_right = self.position - forward * self.radius + right
        return [nose, back_left, back_right]

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
        # Floored at zero. Left to run, both drift further negative every frame
        # of a long run, which is harmless today and is the sort of thing that
        # stops being harmless the moment something starts reading the value.
        self.shot_cooldown_timer = max(0.0, self.shot_cooldown_timer - dt)
        self.invincibility_timer = max(0.0, self.invincibility_timer - dt)
        self.wrap_position()

    def move(self, dt):
        """Slide along the current heading. A negative `dt` reverses.

        `dt` rather than a fixed step, so the ship covers the same ground per
        second whatever the frame rate.
        """
        self.position += self._heading() * PLAYER_SPEED * dt

    def _heading(self):
        """A unit vector pointing where the nose points."""
        return pygame.Vector2(0, 1).rotate(self.rotation)

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
        bullet = Shot(self.position.x, self.position.y)
        bullet.velocity = self._heading() * PLAYER_SHOOT_SPEED
