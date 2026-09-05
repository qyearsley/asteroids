"""Diagnostic logging for a play session.

Two files, both gitignored, both written from the repository's working
directory: `game_state.jsonl` gets one snapshot a second, and
`game_events.jsonl` gets a line whenever something happens. They exist so a
finished run can be read back without a display, which is the only way most of
this game can be inspected at all.

Two properties are deliberate:

- **The caller decides what a snapshot contains.** `log_state` takes a mapping
  of name to sprite group. It used to take nothing and read its caller's locals
  through `inspect.currentframe().f_back.f_locals` -- a boot.dev result-checker
  artifact that became load-bearing on the *shape* of the code above it, because
  renaming a local in `play_run`, or moving the sprite groups into an object,
  silently emptied the log. Passing them in costs one argument and removes the
  constraint.
- **Logging is bounded.** A snapshot is written roughly once a second for
  `_MAX_FRAMES` frames, then stops. `start_run` puts the budget back, so the
  second run of a process logs as fully as the first; without it, logging died
  permanently about sixteen seconds into whichever run happened to be first.

Both files are truncated on the first write of the process and appended to
after that, so one process leaves one file covering every run it played.
"""

from datetime import datetime
import json
import math

__all__ = ["log_state", "log_event", "start_run"]

_FPS = 60
_MAX_SECONDS = 16
# Snapshots are counted in frames, not seconds: this is a frame budget that
# happens to be about sixteen seconds at a steady 60 FPS. A paused frame costs
# the same as a played one.
_MAX_FRAMES = _FPS * _MAX_SECONDS
_SPRITE_SAMPLE_LIMIT = 10  # Maximum number of sprites to log per group.

_frame_count = 0
_state_log_initialized = False
_event_log_initialized = False
_start_time = datetime.now()


def start_run():
    """Begin logging a fresh run: reset the frame budget and the clock.

    Call this once at the top of a run. Without it the frame counter carries
    across runs, so a second game played in the same process was already past
    its budget before it drew a frame and logged nothing at all.
    """
    global _frame_count, _start_time
    _frame_count = 0
    _start_time = datetime.now()


def _describe(sprite):
    """One sprite as a plain dict, with only the attributes it actually has."""
    info = {"type": sprite.__class__.__name__}
    if hasattr(sprite, "position"):
        info["pos"] = [round(sprite.position.x, 2), round(sprite.position.y, 2)]
    if hasattr(sprite, "velocity"):
        info["vel"] = [round(sprite.velocity.x, 2), round(sprite.velocity.y, 2)]
    if hasattr(sprite, "radius"):
        info["rad"] = sprite.radius
    if hasattr(sprite, "rotation"):
        info["rot"] = round(sprite.rotation, 2)
    return info


def log_state(groups, screen=None):
    """Write a snapshot of the named sprite groups, about once a second.

    Args:
        groups: Mapping of name to sprite group, e.g. `{"asteroids": asteroids}`.
            Up to `_SPRITE_SAMPLE_LIMIT` sprites are described per group; the
            full count is always recorded.
        screen: The display surface, if there is one, for its size.
    """
    global _frame_count

    if _frame_count > _MAX_FRAMES:
        return

    # Take a snapshot approx. once per second
    _frame_count += 1
    if _frame_count % _FPS != 0:
        return

    now = datetime.now()
    entry = {
        "timestamp": now.strftime("%H:%M:%S.%f")[:-3],
        "elapsed_s": math.floor((now - _start_time).total_seconds()),
        "frame": _frame_count,
        "screen_size": list(screen.get_size()) if screen is not None else [],
    }
    for name, group in groups.items():
        sprites = [_describe(sprite) for i, sprite in enumerate(group) if i < _SPRITE_SAMPLE_LIMIT]
        entry[name] = {"count": len(group), "sprites": sprites}

    _append("game_state.jsonl", entry, "_state_log_initialized")


def log_event(event_type, **details):
    """Write one line to the event log. Cheap, and not rate limited."""
    now = datetime.now()
    event = {
        "timestamp": now.strftime("%H:%M:%S.%f")[:-3],
        "elapsed_s": math.floor((now - _start_time).total_seconds()),
        "frame": _frame_count,
        "type": event_type,
        **details,
    }
    _append("game_events.jsonl", event, "_event_log_initialized")


def _append(path, payload, flag_name):
    """Write one JSON line, truncating the file on this process's first write."""
    initialized = globals()[flag_name]
    with open(path, "w" if not initialized else "a") as f:
        f.write(json.dumps(payload) + "\n")
    globals()[flag_name] = True
