"""Tests for asteroid splitting -- the game's core progression mechanic."""

import pygame
import pytest

from asteroid import Asteroid
from constants import ASTEROID_MIN_RADIUS, ASTEROID_SPLIT_SPEED_MULTIPLIER


@pytest.fixture
def asteroids(container_for):
    return container_for(Asteroid)


def splittable():
    """An asteroid larger than the minimum radius, so `split()` produces children."""
    asteroid = Asteroid(300, 200, ASTEROID_MIN_RADIUS * 2)
    asteroid.velocity = pygame.Vector2(100, 0)
    return asteroid


def test_smallest_asteroid_is_destroyed_without_splitting(asteroids):
    Asteroid(300, 200, ASTEROID_MIN_RADIUS).split()
    assert len(asteroids) == 0


def test_larger_asteroid_splits_into_two_one_size_smaller(asteroids):
    asteroid = splittable()
    asteroid.split()
    children = list(asteroids)
    assert len(children) == 2
    assert all(child.radius == asteroid.radius - ASTEROID_MIN_RADIUS for child in children)


def test_children_start_where_the_parent_died(asteroids):
    asteroid = splittable()
    asteroid.split()
    assert all(child.position == asteroid.position for child in asteroids)


def test_children_speed_up_by_the_split_multiplier(asteroids):
    asteroid = splittable()
    expected_speed = asteroid.velocity.length() * ASTEROID_SPLIT_SPEED_MULTIPLIER
    asteroid.split()
    assert all(child.velocity.length() == pytest.approx(expected_speed) for child in asteroids)


def test_children_deflect_in_opposite_directions(asteroids):
    asteroid = splittable()
    heading = pygame.Vector2(asteroid.velocity)
    asteroid.split()
    first, second = asteroids
    assert heading.angle_to(first.velocity) == pytest.approx(-heading.angle_to(second.velocity))
