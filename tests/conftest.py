"""Shared fixtures for the asteroids tests.

The game has no display dependency in its logic, so these tests run headless —
no `pygame.init()` or `set_mode()` required.
"""

import pygame
import pytest


@pytest.fixture
def container_for():
    """Return a factory that gives a sprite class a fresh container group.

    Game objects auto-register with `cls.containers` when constructed, which is
    how `main()` collects them. Tests use the returned group to inspect objects
    created indirectly -- asteroid splits, shots, explosion particles.
    """
    patched = []

    def attach(cls):
        group = pygame.sprite.Group()
        cls.containers = (group,)
        patched.append(cls)
        return group

    yield attach

    for cls in patched:
        del cls.containers
