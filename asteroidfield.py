import pygame

from asteroid import Asteroid
from constants import (
    ASTEROID_KINDS,
    ASTEROID_MAX_RADIUS,
    ASTEROID_MIN_RADIUS,
    ASTEROID_RAMP_SECONDS,
    ASTEROID_SPAWN_RATE_FLOOR,
    ASTEROID_SPAWN_RATE_SECONDS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
import rng


class AsteroidField(pygame.sprite.Sprite):
    # Define spawn edges: [velocity_direction, position_function]
    # Asteroids spawn just off-screen and move inward
    edges = [
        [
            pygame.Vector2(1, 0),  # Move right
            lambda y: pygame.Vector2(-ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT),  # Spawn on left edge
        ],
        [
            pygame.Vector2(-1, 0),  # Move left
            lambda y: pygame.Vector2(
                SCREEN_WIDTH + ASTEROID_MAX_RADIUS,
                y * SCREEN_HEIGHT,  # Spawn on right edge
            ),
        ],
        [
            pygame.Vector2(0, 1),  # Move down
            lambda x: pygame.Vector2(x * SCREEN_WIDTH, -ASTEROID_MAX_RADIUS),  # Spawn on top edge
        ],
        [
            pygame.Vector2(0, -1),  # Move up
            lambda x: pygame.Vector2(
                x * SCREEN_WIDTH,
                SCREEN_HEIGHT + ASTEROID_MAX_RADIUS,  # Spawn on bottom edge
            ),
        ],
    ]

    def __init__(self):
        # Guarded like CircleShape.__init__, rather than assuming the caller
        # assigned `containers` first. The two used to disagree, so a field
        # built without them raised AttributeError while every other sprite
        # simply went ungrouped.
        if hasattr(self, "containers"):
            pygame.sprite.Sprite.__init__(self, self.containers)
        else:
            pygame.sprite.Sprite.__init__(self)
        self.spawn_timer = 0.0
        self.elapsed = 0.0

    def spawn_interval(self):
        """Seconds between spawns right now, which shortens as a run goes on.

        A straight line from ASTEROID_SPAWN_RATE_SECONDS down to
        ASTEROID_SPAWN_RATE_FLOOR over ASTEROID_RAMP_SECONDS, then flat. The
        interval was a constant before this, so a classic run at minute ten
        asked exactly as much of the player as minute one -- the field grew, but
        only because nothing had cleared it.
        """
        progress = min(1.0, self.elapsed / ASTEROID_RAMP_SECONDS)
        span = ASTEROID_SPAWN_RATE_SECONDS - ASTEROID_SPAWN_RATE_FLOOR
        return ASTEROID_SPAWN_RATE_SECONDS - span * progress

    def spawn(self, radius, position, velocity):
        asteroid = Asteroid(position.x, position.y, radius)
        asteroid.velocity = velocity
        return asteroid

    def update(self, dt):
        self.elapsed += dt
        self.spawn_timer += dt
        interval = self.spawn_interval()
        if self.spawn_timer > interval:
            # Carry the overshoot rather than dropping it. Zeroing the timer
            # quantized the real interval to whole frames and made it drift
            # slightly long, which is the sort of thing that makes two runs on
            # one seed stop matching.
            self.spawn_timer -= interval

            # Spawn a new asteroid at a random edge
            edge = rng.spawns.choice(self.edges)
            speed = rng.spawns.randint(40, 100)
            velocity = edge[0] * speed
            velocity = velocity.rotate(rng.spawns.randint(-30, 30))
            position = edge[1](rng.spawns.uniform(0, 1))
            kind = rng.spawns.randint(1, ASTEROID_KINDS)
            self.spawn(ASTEROID_MIN_RADIUS * kind, position, velocity)
