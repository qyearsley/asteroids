"""Tests for the geometry shared by every game object: screen wrap, collision."""

import pygame
import pytest

from circleshape import CircleShape
from constants import SCREEN_HEIGHT, SCREEN_WIDTH


class TestWrapPosition:
    @pytest.mark.parametrize(
        "start,expected",
        [
            ((-1, 100), (SCREEN_WIDTH - 1, 100)),
            ((SCREEN_WIDTH + 1, 100), (1, 100)),
            ((100, -1), (100, SCREEN_HEIGHT - 1)),
            ((100, SCREEN_HEIGHT + 1), (100, 1)),
        ],
        ids=["off-left", "off-right", "off-top", "off-bottom"],
    )
    def test_wraps_to_the_opposite_edge(self, start, expected):
        shape = CircleShape(*start, 10)
        shape.wrap_position()
        assert shape.position == pygame.Vector2(expected)

    def test_leaves_an_on_screen_position_alone(self):
        shape = CircleShape(640, 360, 10)
        shape.wrap_position()
        assert shape.position == pygame.Vector2(640, 360)

    def test_wraps_both_axes_at_a_corner(self):
        shape = CircleShape(-5, -5, 10)
        shape.wrap_position()
        assert shape.position == pygame.Vector2(SCREEN_WIDTH - 5, SCREEN_HEIGHT - 5)


class TestCollidesWith:
    def test_overlapping_circles_collide(self):
        assert CircleShape(0, 0, 10).collides_with(CircleShape(15, 0, 10))

    def test_separated_circles_do_not_collide(self):
        assert not CircleShape(0, 0, 10).collides_with(CircleShape(100, 0, 10))

    def test_exactly_touching_circles_do_not_collide(self):
        # The check is a strict `<`, so grazing at exactly r1 + r2 counts as a miss.
        assert not CircleShape(0, 0, 10).collides_with(CircleShape(30, 0, 20))
