"""Shared fixtures for the asteroids tests.

The game has no display dependency in its logic, so these tests run headless —
no `pygame.init()` or `set_mode()` required.
"""

import pygame
import pytest

import logger


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

    # A class attribute cannot be popped -- `cls.__dict__` is a mappingproxy --
    # and a test that attaches the same class twice would make a plain `del`
    # raise during teardown, turning a passing test into a confusing error in
    # the fixture. Deduplicate instead.
    for cls in dict.fromkeys(patched):
        del cls.containers


@pytest.fixture(autouse=True)
def _no_disk_logging(request, monkeypatch):
    """Keep the diagnostic logger off the filesystem for the whole suite.

    `logger` writes `game_state.jsonl` and `game_events.jsonl` to the working
    directory with no way to switch it off, and several modules call it during
    ordinary gameplay. Two test files used to muzzle it one at a time and the
    rest simply wrote files; this does it once, for everything.

    `tests/test_logger.py` is testing the writer itself, so it opts out with
    `@pytest.mark.real_logger` and intercepts `open` instead.
    """
    if request.node.get_closest_marker("real_logger"):
        return
    monkeypatch.setattr(logger, "log_event", lambda *args, **kwargs: None)
    monkeypatch.setattr(logger, "log_state", lambda *args, **kwargs: None)
