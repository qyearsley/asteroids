"""Tests for the spawner: asteroids must enter from off-screen, heading inward."""

import pygame
import pytest

from asteroid import Asteroid
import asteroidfield
from asteroidfield import AsteroidField
import constants
from constants import ASTEROID_MIN_RADIUS, SCREEN_HEIGHT, SCREEN_WIDTH


@pytest.fixture
def asteroids(container_for):
    """A group collecting whatever the field spawns."""
    return container_for(Asteroid)


@pytest.fixture
def field(container_for, asteroids):
    """A field wired to that group, ready to be stepped."""
    container_for(AsteroidField)
    return AsteroidField()


# Sampling the ends and middle of each edge is enough to catch an axis mix-up.
POSITIONS_ALONG_EDGE = (0.0, 0.5, 1.0)


@pytest.mark.parametrize("direction,position_for", AsteroidField.edges)
@pytest.mark.parametrize("fraction", POSITIONS_ALONG_EDGE)
def test_asteroids_spawn_outside_the_visible_area(direction, position_for, fraction):
    position = position_for(fraction)
    on_screen = 0 <= position.x <= SCREEN_WIDTH and 0 <= position.y <= SCREEN_HEIGHT
    assert not on_screen


@pytest.mark.parametrize("direction,position_for", AsteroidField.edges)
@pytest.mark.parametrize("fraction", POSITIONS_ALONG_EDGE)
def test_spawn_direction_points_onto_the_screen(direction, position_for, fraction):
    centre = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    # A positive dot product means the asteroid is drifting toward the centre
    # rather than away from it.
    assert direction.dot(centre - position_for(fraction)) > 0


def test_spawn_creates_an_asteroid_with_the_requested_motion(container_for):
    asteroids = container_for(Asteroid)
    container_for(AsteroidField)
    field = AsteroidField()

    field.spawn(ASTEROID_MIN_RADIUS, pygame.Vector2(10, 20), pygame.Vector2(3, 4))

    (asteroid,) = asteroids
    assert asteroid.radius == ASTEROID_MIN_RADIUS
    assert asteroid.position == pygame.Vector2(10, 20)
    assert asteroid.velocity == pygame.Vector2(3, 4)


class TestDifficultyRamp:
    """The spawn interval shortens as a run goes on, then holds at a floor.

    It used to be the constant `ASTEROID_SPAWN_RATE_SECONDS` and nothing ever
    changed it, so minute ten of a classic run asked exactly as much of the
    player as minute one: the field grew, but only because nothing had cleared
    it. These hold the shape of the curve rather than its numbers, so retuning
    the two constants does not rewrite the tests.
    """

    def test_starts_at_the_configured_rate(self, field):
        assert field.spawn_interval() == pytest.approx(constants.ASTEROID_SPAWN_RATE_SECONDS)

    def test_shortens_as_the_run_goes_on(self, field):
        opening = field.spawn_interval()
        field.elapsed = constants.ASTEROID_RAMP_SECONDS / 2
        midway = field.spawn_interval()
        assert midway < opening

    def test_never_gets_slower(self, field):
        seen = []
        for step in range(0, int(constants.ASTEROID_RAMP_SECONDS) + 60, 10):
            field.elapsed = step
            seen.append(field.spawn_interval())
        assert seen == sorted(seen, reverse=True)

    def test_reaches_the_floor_at_the_end_of_the_ramp(self, field):
        field.elapsed = constants.ASTEROID_RAMP_SECONDS
        assert field.spawn_interval() == pytest.approx(constants.ASTEROID_SPAWN_RATE_FLOOR)

    def test_holds_at_the_floor_rather_than_going_below_it(self, field):
        field.elapsed = constants.ASTEROID_RAMP_SECONDS * 10
        assert field.spawn_interval() == pytest.approx(constants.ASTEROID_SPAWN_RATE_FLOOR)

    def test_a_long_run_spawns_more_than_a_short_one_over_the_same_span(self, field, asteroids):
        def spawns_over(seconds, start_at):
            asteroids.empty()
            field.elapsed = start_at
            field.spawn_timer = 0.0
            for _ in range(int(seconds / 0.05)):
                field.update(0.05)
            return len(asteroids)

        early = spawns_over(20, start_at=0)
        late = spawns_over(20, start_at=constants.ASTEROID_RAMP_SECONDS)
        assert late > early


class TestSpawnTiming:
    def test_carries_the_overshoot_instead_of_dropping_it(self, field, asteroids):
        # Zeroing the timer threw away whatever the frame overshot by, which
        # quantized the real interval to whole frames and made it drift long --
        # and that is how two runs on one seed stop matching. The residue is not
        # pinned to an exact figure because the interval itself moves as the
        # ramp advances; what matters is that some of the overshoot survives.
        interval = field.spawn_interval()
        field.update(interval * 1.75)
        assert len(asteroids) == 1
        assert 0 < field.spawn_timer < interval
        assert field.spawn_timer == pytest.approx(interval * 0.75, rel=0.05)

    def test_one_long_frame_still_only_spawns_once(self, field, asteroids):
        # A dropped frame should not empty the whole backlog at once.
        field.update(field.spawn_interval() * 5)
        assert len(asteroids) == 1


def test_a_field_built_without_containers_does_not_raise():
    # CircleShape guards this and AsteroidField did not, so the same mistake
    # produced two different outcomes depending on which class you made.
    original = getattr(asteroidfield.AsteroidField, "containers", None)
    if original is not None:
        del asteroidfield.AsteroidField.containers
    try:
        asteroidfield.AsteroidField()
    finally:
        if original is not None:
            asteroidfield.AsteroidField.containers = original
