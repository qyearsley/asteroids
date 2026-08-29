"""Local best results, saved to a small JSON file next to the game.

Results are keyed by mode and then by seed, so a time trial on seed 1234 is
only ever compared against other runs of seed 1234. Runs played without a seed
all share one bucket -- they aren't comparable to each other anyway.

The file is separate from the logger's `game_state.jsonl` and
`game_events.jsonl`, which belong to the boot.dev result checker.
"""

import json

from constants import BEST_RESULTS_FILE, MODE_TIME_TRIAL


def load(path=BEST_RESULTS_FILE):
    """Read the saved bests. A missing or damaged file just means no bests yet."""
    try:
        with open(path) as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save(results, path=BEST_RESULTS_FILE):
    """Write the bests back out, formatted so the file stays readable by hand."""
    with open(path, "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)
        f.write("\n")


def seed_key(seed):
    """JSON keys are strings, and unseeded runs share the one bucket."""
    return "random" if seed is None else str(seed)


def best_for(results, mode, seed):
    """The stored best for this mode and seed, or None."""
    return results.get(mode, {}).get(seed_key(seed))


def beats(mode, result, previous):
    """Is `result` an improvement on `previous` (which may be None)?"""
    if mode == MODE_TIME_TRIAL:
        # A trial that ran out of lives never counts, however fast it was.
        if not result["completed"]:
            return False
        return previous is None or result["time"] < previous["time"]
    return previous is None or result["score"] > previous["score"]


def record(mode, seed, result, path=BEST_RESULTS_FILE):
    """Save `result` if it beats the stored best.

    Returns `(improved, previous_best)` so the end-of-run screen can say whether
    this was a record and what there is to beat.
    """
    results = load(path)
    previous = best_for(results, mode, seed)
    improved = beats(mode, result, previous)
    if improved:
        results.setdefault(mode, {})[seed_key(seed)] = result
        save(results, path)
    return improved, previous
