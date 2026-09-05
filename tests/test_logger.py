"""Tests for the diagnostic logger.

Previously untested, and the most fragile module in the repo: global counters,
a frame budget, and unconditional writes to the working directory. Every test
here redirects `open` to an in-memory buffer, so nothing reaches disk.

These are also the tests that hold the two behaviours the logger got wrong. It
used to read its caller's locals through `inspect`, which made every local name
in `play_run` part of its interface; and its frame counter was never reset, so
the second run in a process logged nothing at all.
"""

import io
import json

import pygame
import pytest

import logger

pytestmark = pytest.mark.real_logger


class _Sprite:
    """The shape `_describe` reads: any of these attributes, or none of them."""

    def __init__(self, x=0.0, y=0.0, vx=0.0, vy=0.0, radius=None, rotation=None):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(vx, vy)
        if radius is not None:
            self.radius = radius
        if rotation is not None:
            self.rotation = rotation


class _Bare:
    """A sprite with no position, velocity, radius or rotation at all."""


class _Capture(io.StringIO):
    """A file-like object that hands its contents to a sink when closed."""

    def __init__(self, path, mode, sink):
        super().__init__()
        self._path = path
        self._mode = mode
        self._sink = sink

    def close(self):
        self._sink.setdefault(self._path, []).append((self._mode, self.getvalue()))
        super().close()


@pytest.fixture
def written(monkeypatch):
    """Capture everything the logger writes, keyed by filename.

    The whole file carries `real_logger`, so conftest leaves `log_state` and
    `log_event` alone here; this intercepts the write instead, and resets the
    module-level counters so each test starts from a clean logger.
    """
    files = {}
    monkeypatch.setattr(
        "builtins.open", lambda path, mode="r", *a, **k: _Capture(path, mode, files)
    )
    monkeypatch.setattr(logger, "_frame_count", 0)
    monkeypatch.setattr(logger, "_state_log_initialized", False)
    monkeypatch.setattr(logger, "_event_log_initialized", False)
    return files


def lines(written, path):
    """Every JSON object written to `path`, in order."""
    return [json.loads(text) for _mode, text in written.get(path, []) if text.strip()]


def modes(written, path):
    """The file mode of each write to `path`: "w" truncates, "a" appends."""
    return [mode for mode, _text in written.get(path, [])]


def group(*sprites):
    """A stand-in for a pygame sprite group: iterable, with a length."""
    return list(sprites)


class TestLogState:
    def test_writes_nothing_until_a_full_second_of_frames(self, written):
        for _ in range(logger._FPS - 1):
            logger.log_state({"asteroids": group(_Sprite())})
        assert lines(written, "game_state.jsonl") == []

    def test_writes_one_snapshot_per_second_of_frames(self, written):
        for _ in range(logger._FPS * 3):
            logger.log_state({"asteroids": group(_Sprite())})
        assert len(lines(written, "game_state.jsonl")) == 3

    def test_records_the_group_name_the_caller_chose(self, written):
        for _ in range(logger._FPS):
            logger.log_state({"rocks": group(_Sprite(), _Sprite())})
        entry = lines(written, "game_state.jsonl")[0]
        assert entry["rocks"]["count"] == 2

    def test_counts_every_sprite_but_samples_only_a_few(self, written):
        many = group(*[_Sprite() for _ in range(logger._SPRITE_SAMPLE_LIMIT + 5)])
        for _ in range(logger._FPS):
            logger.log_state({"asteroids": many})
        entry = lines(written, "game_state.jsonl")[0]
        assert entry["asteroids"]["count"] == len(many)
        assert len(entry["asteroids"]["sprites"]) == logger._SPRITE_SAMPLE_LIMIT

    def test_describes_only_the_attributes_a_sprite_has(self, written):
        for _ in range(logger._FPS):
            logger.log_state({"mixed": group(_Sprite(1, 2, 3, 4, radius=5, rotation=6), _Bare())})
        described = lines(written, "game_state.jsonl")[0]["mixed"]["sprites"]
        assert described[0] == {
            "type": "_Sprite",
            "pos": [1.0, 2.0],
            "vel": [3.0, 4.0],
            "rad": 5,
            "rot": 6,
        }
        assert described[1] == {"type": "_Bare"}

    def test_screen_size_is_empty_when_no_screen_is_passed(self, written):
        for _ in range(logger._FPS):
            logger.log_state({"asteroids": group()})
        assert lines(written, "game_state.jsonl")[0]["screen_size"] == []

    def test_screen_size_comes_from_the_surface_when_one_is_passed(self, written):
        class _Screen:
            def get_size(self):
                return (1280, 720)

        for _ in range(logger._FPS):
            logger.log_state({"asteroids": group()}, _Screen())
        assert lines(written, "game_state.jsonl")[0]["screen_size"] == [1280, 720]

    def test_stops_once_the_frame_budget_is_spent(self, written):
        for _ in range(logger._MAX_FRAMES + logger._FPS * 3):
            logger.log_state({"asteroids": group()})
        # One per second up to the budget, and nothing after it.
        assert len(lines(written, "game_state.jsonl")) == logger._MAX_FRAMES // logger._FPS

    def test_truncates_on_the_first_write_and_appends_after(self, written):
        for _ in range(logger._FPS * 2):
            logger.log_state({"asteroids": group()})
        assert modes(written, "game_state.jsonl") == ["w", "a"]


class TestStartRun:
    def test_puts_the_frame_budget_back(self, written):
        # The bug this exists for: a second run in the same process was already
        # past its budget before it drew a frame, so it logged nothing at all.
        for _ in range(logger._MAX_FRAMES + 1):
            logger.log_state({"asteroids": group()})
        before = len(lines(written, "game_state.jsonl"))

        logger.start_run()
        for _ in range(logger._FPS):
            logger.log_state({"asteroids": group()})

        assert len(lines(written, "game_state.jsonl")) == before + 1

    def test_restarts_the_frame_number_a_snapshot_reports(self, written):
        for _ in range(logger._FPS * 2):
            logger.log_state({"asteroids": group()})
        logger.start_run()
        for _ in range(logger._FPS):
            logger.log_state({"asteroids": group()})

        frames = [entry["frame"] for entry in lines(written, "game_state.jsonl")]
        assert frames == [logger._FPS, logger._FPS * 2, logger._FPS]

    def test_does_not_truncate_the_file_a_previous_run_wrote(self, written):
        for _ in range(logger._FPS):
            logger.log_state({"asteroids": group()})
        logger.start_run()
        for _ in range(logger._FPS):
            logger.log_state({"asteroids": group()})
        # One file per process, not one per run: the second run appends.
        assert modes(written, "game_state.jsonl") == ["w", "a"]


class TestLogEvent:
    def test_writes_the_type_and_any_details(self, written):
        logger.log_event("asteroid_shot", kind=2, score=50)
        entry = lines(written, "game_events.jsonl")[0]
        assert entry["type"] == "asteroid_shot"
        assert entry["kind"] == 2
        assert entry["score"] == 50

    def test_is_not_rate_limited(self, written):
        for _ in range(5):
            logger.log_event("player_hit")
        assert len(lines(written, "game_events.jsonl")) == 5

    def test_carries_the_frame_the_state_log_is_counting(self, written):
        for _ in range(7):
            logger.log_state({"asteroids": group()})
        logger.log_event("player_hit")
        assert lines(written, "game_events.jsonl")[0]["frame"] == 7

    def test_truncates_on_the_first_write_and_appends_after(self, written):
        logger.log_event("one")
        logger.log_event("two")
        assert modes(written, "game_events.jsonl") == ["w", "a"]

    def test_the_two_logs_keep_separate_files(self, written):
        for _ in range(logger._FPS):
            logger.log_state({"asteroids": group()})
        logger.log_event("player_hit")
        assert set(written) == {"game_state.jsonl", "game_events.jsonl"}
