"""Tests for seeded runs: the same seed has to produce the same asteroids."""

import pygame
import pytest

from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import ASTEROID_MIN_RADIUS, ASTEROID_SPAWN_RATE_SECONDS
import rng

# Each update longer than the spawn rate produces exactly one asteroid.
A_SPAWN_STEP = ASTEROID_SPAWN_RATE_SECONDS + 0.01


def describe(asteroid):
    """The parts of an asteroid two runs have to agree on to be comparable."""
    return (
        asteroid.radius,
        round(asteroid.position.x, 6),
        round(asteroid.position.y, 6),
        round(asteroid.velocity.x, 6),
        round(asteroid.velocity.y, 6),
    )


def spawn_sequence(seed, asteroids, count=5, disturb=False):
    """Seed a run, spawn `count` asteroids, and describe them in arrival order.

    With `disturb`, draw from the effects stream between spawns -- the way a
    player firing at things would.
    """
    asteroids.empty()
    rng.reseed(seed)
    field = AsteroidField()
    for _ in range(count):
        field.update(A_SPAWN_STEP)
        if disturb:
            rng.effects.uniform(0, 360)
    return [describe(asteroid) for asteroid in asteroids]


@pytest.fixture
def asteroids(container_for):
    container_for(AsteroidField)
    return container_for(Asteroid)


def test_the_same_seed_replays_the_same_asteroids(asteroids):
    assert spawn_sequence(1234, asteroids) == spawn_sequence(1234, asteroids)


def test_different_seeds_give_different_asteroids(asteroids):
    assert spawn_sequence(1234, asteroids) != spawn_sequence(5678, asteroids)


def test_without_a_seed_runs_differ(asteroids):
    assert spawn_sequence(None, asteroids) != spawn_sequence(None, asteroids)


def test_explosions_and_splits_do_not_shift_the_spawn_sequence(asteroids):
    # Separate streams are the point: two players on one seed must meet the
    # same asteroids no matter how differently they play.
    undisturbed = spawn_sequence(99, asteroids)
    assert spawn_sequence(99, asteroids, disturb=True) == undisturbed


def test_splits_are_repeatable_under_the_same_seed(container_for):
    asteroids = container_for(Asteroid)

    def children_of_a_split():
        asteroids.empty()
        parent = Asteroid(300, 200, ASTEROID_MIN_RADIUS * 2)
        parent.velocity = pygame.Vector2(100, 0)
        parent.split()
        return [describe(child) for child in asteroids]

    rng.reseed(7)
    first = children_of_a_split()
    rng.reseed(7)
    assert children_of_a_split() == first


def test_a_seed_gives_two_independent_streams():
    rng.reseed(3)
    assert rng.spawns.random() != rng.effects.random()


def test_random_seed_is_short_enough_to_retype():
    assert 0 <= rng.random_seed() < 1_000_000
