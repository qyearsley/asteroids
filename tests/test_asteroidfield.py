"""Tests for the spawner: asteroids must enter from off-screen, heading inward."""

import pygame
import pytest

from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import ASTEROID_MIN_RADIUS, SCREEN_HEIGHT, SCREEN_WIDTH

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
