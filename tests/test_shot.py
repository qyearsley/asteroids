"""Tests for bullets: how they move, and how they stop existing.

`Shot` had no tests at all, which is why it went so long without a lifetime --
a bullet used to wrap at the screen edge and fly until it hit something, so a
run accumulated one more permanent sprite every 0.3 seconds.
"""

import pygame
import pytest

from constants import (
    PLAYER_SHOOT_SPEED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHOT_LIFETIME_SECONDS,
    SHOT_RADIUS,
)
from shot import Shot


@pytest.fixture
def shots(container_for):
    return container_for(Shot)


def moving_shot(x=100, y=100, vx=500, vy=0):
    shot = Shot(x, y)
    shot.velocity = pygame.Vector2(vx, vy)
    return shot


def shot_update(shots, dt):
    """Advance every live shot in the group by `dt`."""
    for shot in list(shots):
        shot.update(dt)


def test_a_new_shot_has_the_configured_radius_and_a_full_life():
    shot = Shot(10, 20)
    assert shot.radius == SHOT_RADIUS
    assert shot.life_left == SHOT_LIFETIME_SECONDS


def test_it_travels_at_its_own_velocity():
    shot = moving_shot(x=100, y=100, vx=500, vy=0)
    shot.update(0.1)
    assert shot.position.x == pytest.approx(150)
    assert shot.position.y == pytest.approx(100)


def test_it_wraps_at_the_screen_edge_while_it_still_has_life(shots):
    shot = moving_shot(x=SCREEN_WIDTH - 10, y=100, vx=500, vy=0)
    shot.update(0.1)
    assert shot.position.x < SCREEN_WIDTH
    assert shot in shots


def test_it_survives_right_up_to_its_lifetime(shots):
    shot = moving_shot()
    shot.update(SHOT_LIFETIME_SECONDS - 0.01)
    assert shot in shots


def test_it_removes_itself_once_its_lifetime_runs_out(shots):
    shot = moving_shot()
    shot.update(SHOT_LIFETIME_SECONDS)
    assert shot not in shots


def test_an_expired_shot_stops_where_it_died_rather_than_moving_first(shots):
    # The kill comes before the move, so a dead bullet never draws one more
    # frame's worth of travel on its way out.
    shot = moving_shot(x=100, y=100, vx=500, vy=0)
    shot.update(SHOT_LIFETIME_SECONDS + 1)
    assert shot.position == pygame.Vector2(100, 100)


def test_lifetime_is_spent_across_several_frames(shots):
    moving_shot()
    # A tenth at a time, so the kill has to come from the accumulated total
    # rather than from any single frame being long enough on its own.
    step = SHOT_LIFETIME_SECONDS / 10
    for _ in range(9):
        shot_update(shots, step)
    assert len(shots) == 1
    shot_update(shots, step * 2)
    assert len(shots) == 0


def test_a_shot_can_cross_the_screen_before_it_expires():
    # The lifetime is a reach, not a leash: it has to be long enough that
    # shooting across the play area is still a thing you can do.
    reach = PLAYER_SHOOT_SPEED * SHOT_LIFETIME_SECONDS
    assert reach > min(SCREEN_WIDTH, SCREEN_HEIGHT) / 2
