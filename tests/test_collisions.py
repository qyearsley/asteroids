"""Tests for `resolve_collisions`, the frame of the game where scoring happens.

Split out of `play_run` so it could be tested at all. The main loop needs a
display; this does not, and it is where the double-scoring bug lived: the shot
loop had no `break`, so two bullets landing on one asteroid in the same frame
scored it twice, split it twice -- four children instead of two -- and drew two
explosions.
"""

import pygame
import pytest

import asteroid
import constants
import main
import particle
import player
import shot


@pytest.fixture
def field(container_for):
    """Every group the collision pass reads or writes, wired up."""
    asteroids = container_for(asteroid.Asteroid)
    shots = container_for(shot.Shot)
    container_for(particle.Particle)
    container_for(player.Player)
    return asteroids, shots


def a_rock(asteroids, x=100, y=100, radius=constants.ASTEROID_MIN_RADIUS):
    """An asteroid sitting still at `(x, y)`. Registers itself with the group."""
    rock = asteroid.Asteroid(x, y, radius)
    rock.velocity = pygame.Vector2(0, 0)
    return rock


def a_bullet(shots, x=100, y=100):
    """A bullet sitting still at `(x, y)`. Registers itself with the group."""
    bullet = shot.Shot(x, y)
    bullet.velocity = pygame.Vector2(0, 0)
    return bullet


def a_ship(x=1000, y=1000):
    """A ship, parked well away from where the rocks go unless a test says otherwise."""
    return player.Player(x, y)


class TestShootingAnAsteroid:
    def test_a_hit_scores_and_counts(self, field):
        asteroids, shots = field
        a_rock(asteroids)
        a_bullet(shots)

        hits, points, destroyed = main.resolve_collisions(a_ship(), asteroids, shots)

        assert hits == 0
        assert destroyed == 1
        assert points == constants.SCORE_PER_ASTEROID[1]

    def test_a_hit_removes_the_bullet(self, field):
        asteroids, shots = field
        a_rock(asteroids)
        a_bullet(shots)

        main.resolve_collisions(a_ship(), asteroids, shots)

        assert len(shots) == 0

    def test_a_larger_asteroid_is_worth_less(self, field):
        asteroids, shots = field
        a_rock(asteroids, radius=constants.ASTEROID_MIN_RADIUS * 3)
        a_bullet(shots)

        _hits, points, _destroyed = main.resolve_collisions(a_ship(), asteroids, shots)

        assert points == constants.SCORE_PER_ASTEROID[3]
        assert points < constants.SCORE_PER_ASTEROID[1]

    def test_a_large_asteroid_leaves_two_children(self, field):
        asteroids, shots = field
        a_rock(asteroids, radius=constants.ASTEROID_MIN_RADIUS * 2)
        a_bullet(shots)

        main.resolve_collisions(a_ship(), asteroids, shots)

        assert len(asteroids) == 2

    def test_a_miss_costs_nothing(self, field):
        asteroids, shots = field
        a_rock(asteroids, x=100, y=100)
        a_bullet(shots, x=900, y=600)

        hits, points, destroyed = main.resolve_collisions(a_ship(), asteroids, shots)

        assert (hits, points, destroyed) == (0, 0, 0)
        assert len(shots) == 1
        assert len(asteroids) == 1

    def test_two_separate_asteroids_are_both_scored(self, field):
        asteroids, shots = field
        a_rock(asteroids, x=100, y=100)
        a_rock(asteroids, x=600, y=400)
        a_bullet(shots, x=100, y=100)
        a_bullet(shots, x=600, y=400)

        _hits, points, destroyed = main.resolve_collisions(a_ship(), asteroids, shots)

        assert destroyed == 2
        assert points == constants.SCORE_PER_ASTEROID[1] * 2


class TestTwoBulletsOnOneAsteroid:
    """The bug the `break` fixes. Every assertion here failed before it."""

    def test_it_is_scored_once(self, field):
        asteroids, shots = field
        a_rock(asteroids, radius=constants.ASTEROID_MIN_RADIUS * 2)
        a_bullet(shots)
        a_bullet(shots)

        _hits, points, destroyed = main.resolve_collisions(a_ship(), asteroids, shots)

        assert destroyed == 1
        assert points == constants.SCORE_PER_ASTEROID[2]

    def test_it_splits_into_two_children_and_not_four(self, field):
        asteroids, shots = field
        a_rock(asteroids, radius=constants.ASTEROID_MIN_RADIUS * 2)
        a_bullet(shots)
        a_bullet(shots)

        main.resolve_collisions(a_ship(), asteroids, shots)

        assert len(asteroids) == 2

    def test_only_the_first_bullet_is_spent(self, field):
        # The second one is still in the air, which is the honest outcome: it
        # never reached anything, because the thing it was aimed at is gone.
        asteroids, shots = field
        a_rock(asteroids)
        a_bullet(shots)
        a_bullet(shots)

        main.resolve_collisions(a_ship(), asteroids, shots)

        assert len(shots) == 1


class TestHittingTheShip:
    def test_flying_into_an_asteroid_costs_a_life(self, field):
        asteroids, shots = field
        a_rock(asteroids, x=300, y=300)
        ship = a_ship(300, 300)
        ship.invincibility_timer = 0

        hits, _points, _destroyed = main.resolve_collisions(ship, asteroids, shots)

        assert hits == 1

    def test_the_ship_respawns_after_a_hit(self, field):
        asteroids, shots = field
        a_rock(asteroids, x=300, y=300)
        ship = a_ship(300, 300)
        ship.invincibility_timer = 0

        main.resolve_collisions(ship, asteroids, shots)

        assert ship.position == pygame.Vector2(
            constants.SCREEN_WIDTH / 2, constants.SCREEN_HEIGHT / 2
        )
        assert ship.invincibility_timer > 0

    def test_an_invincible_ship_is_not_hit(self, field):
        asteroids, shots = field
        a_rock(asteroids, x=300, y=300)
        ship = a_ship(300, 300)
        ship.invincibility_timer = constants.PLAYER_INVINCIBILITY_SECONDS

        hits, _points, _destroyed = main.resolve_collisions(ship, asteroids, shots)

        assert hits == 0

    def test_the_asteroid_that_hit_the_ship_survives(self, field):
        # Ramming does not clear the rock: it is still there when you respawn.
        asteroids, shots = field
        a_rock(asteroids, x=300, y=300)
        ship = a_ship(300, 300)
        ship.invincibility_timer = 0

        main.resolve_collisions(ship, asteroids, shots)

        assert len(asteroids) == 1


class TestNothingHappening:
    def test_an_empty_field_reports_nothing(self, field):
        asteroids, shots = field
        assert main.resolve_collisions(a_ship(), asteroids, shots) == (0, 0, 0)

    def test_asteroids_with_no_bullets_report_nothing(self, field):
        asteroids, _shots = field
        a_rock(asteroids)
        a_rock(asteroids, x=400)
        assert main.resolve_collisions(a_ship(), asteroids, _shots) == (0, 0, 0)
