"""Tests for the player ship: hull geometry, shooting cooldown, and respawn."""

import pygame
import pytest

from constants import (
    PLAYER_INVINCIBILITY_SECONDS,
    PLAYER_SHOOT_SPEED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from player import Player
from shot import Shot


@pytest.fixture
def shots(container_for):
    return container_for(Shot)


def nose_direction(player):
    """The unit-ish vector from the ship's centre to the tip of its hull."""
    return player.triangle()[0] - player.position


class TestTriangle:
    def test_nose_sits_one_radius_ahead_of_the_centre(self):
        player = Player(100, 100)
        nose, back_left, back_right = player.triangle()
        assert player.position.distance_to(nose) == pytest.approx(player.radius)
        assert player.position.distance_to(back_left) == pytest.approx(
            player.position.distance_to(back_right)
        )

    def test_hull_turns_with_the_ship(self):
        upright = Player(100, 100)
        turned = Player(100, 100)
        turned.rotation = 90
        assert abs(nose_direction(upright).angle_to(nose_direction(turned))) == pytest.approx(90)


class TestShoot:
    def test_fires_a_single_shot_at_the_configured_speed(self, shots):
        player = Player(100, 100)
        player.shoot()
        (shot,) = shots
        assert shot.position == player.position
        assert shot.velocity.length() == pytest.approx(PLAYER_SHOOT_SPEED)

    def test_shot_travels_in_the_direction_the_ship_faces(self, shots):
        player = Player(100, 100)
        player.rotation = 135
        player.shoot()
        (shot,) = shots
        assert shot.velocity.angle_to(nose_direction(player)) == pytest.approx(0)

    def test_cooldown_blocks_an_immediate_second_shot(self, shots):
        player = Player(100, 100)
        player.shoot()
        player.shoot()
        assert len(shots) == 1

    def test_firing_resumes_once_the_cooldown_expires(self, shots):
        player = Player(100, 100)
        player.shoot()
        player.shot_cooldown_timer = 0  # `update()` normally drains this each frame
        player.shoot()
        assert len(shots) == 2


def test_respawn_recentres_the_ship_and_grants_invincibility():
    player = Player(10, 10)
    player.velocity = pygame.Vector2(50, 50)
    player.rotation = 200

    player.respawn()

    assert player.position == pygame.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    assert player.velocity == pygame.Vector2(0, 0)
    assert player.rotation == 0
    assert player.invincibility_timer == PLAYER_INVINCIBILITY_SECONDS
