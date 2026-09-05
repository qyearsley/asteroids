# Asteroids

A classic Asteroids arcade game built with Pygame. Course project for [boot.dev](https://www.boot.dev/).

## How to Play

```bash
uv sync
uv run main.py
```

`uv run` is what puts pygame on the path; a bare `python3 main.py` only works
inside an activated virtualenv.

### Modes

- **Classic** (default) -- survive as long as you can. The run ends when you
  lose all three lives.
- **Time trial** -- destroy 25 asteroids as fast as you can. The clock counts
  up, so a lower time is better. Losing all your lives ends the trial
  unfinished.

```bash
uv run main.py                                  # classic
uv run main.py --mode time-trial                # time trial, seed chosen for you
uv run main.py --mode time-trial --seed 1234    # replay a specific asteroid sequence
uv run main.py --seed 1234                      # classic on a fixed sequence
```

| Flag | Meaning |
| --- | --- |
| `--mode {classic,time-trial}` | Which mode to play. Defaults to `classic`. |
| `--seed N` | Seed the asteroid sequence so the run can be replayed and compared. Time trials pick a seed for you if you leave this out, and print it. |

### Controls

- **W / S** -- thrust forward / backward
- **A / D** -- rotate left / right
- **Space** -- shoot
- **P** -- pause and unpause
- **Escape** -- end the current run and go to the results screen
- **Enter** -- start a run from the title screen
- **R** -- play again from the results screen
- **Q** -- quit

Destroy asteroids to survive. Large asteroids split into two smaller ones when
shot, so clearing a big one makes the screen busier before it makes it emptier.
You lose a life when an asteroid hits your ship, and respawn in the middle with
a couple of seconds of invincibility. Bullets fade after
`SHOT_LIFETIME_SECONDS`, so a shot has a reach rather than circling the screen
until it finds something.

There are no waves and no levels. What escalates instead is the spawn rate: it
starts at `ASTEROID_SPAWN_RATE_SECONDS` and shortens towards
`ASTEROID_SPAWN_RATE_FLOOR` over `ASTEROID_RAMP_SECONDS`, then holds there. Both
ends of that curve, and everything else worth tuning, are in
[`constants.py`](constants.py).

The ship has no inertia: it moves while a key is down and stops when it comes
up. Arcade Asteroids drifts, and adding that back is the single largest change
anyone could make to how this feels -- which is why it has not been made
casually.

### Seeds and best results

A seed fixes which asteroids arrive, from where, and how fast, so two runs of
the same seed face the same waves and their times and scores are worth
comparing. Spawning draws from a separate random stream to explosions and
splits, so how you play doesn't change what arrives next. Player input and
frame timing are still your own -- the seed reproduces the asteroid sequence,
not the whole run.

Best results are saved to `best_results.json` in whatever directory you launch
from -- the repo root, if you follow the commands above -- keyed by mode and
seed: fastest time for a time trial, highest score for classic. Runs played
without a seed all share one "random" bucket. The file is gitignored, and is
separate from the logger's files described below.

## Development

```bash
uv run pytest        # Run tests
uv run ruff check .  # Lint
uv run ruff format . # Format
```

All three run on every push and every pull request; see
[`.github/workflows/ci.yml`](.github/workflows/ci.yml). CI installs from the
lockfile, so it checks the same versions a developer has rather than resolving
afresh.

Tests in [`tests/`](tests/) cover the parts of the game that don't need a
display, which is almost all of it: screen wrapping and collision
(`circleshape`), asteroid splitting, spawn geometry and the difficulty ramp,
hull geometry and the shooting cooldown, bullet lifetimes, particle lifetimes,
seeded spawn sequences (`rng`), the best-results store (`bestresults`), the
diagnostic logger, and in `main` both the argument parsing and run summaries and
`resolve_collisions` -- the frame of the game where scoring happens. That last
one was pulled out of the main loop specifically so it could be tested; it is
where a missing `break` used to score one asteroid twice when two bullets
reached it in the same frame.

What is left untested is genuinely display-bound: keyboard handling in
`Player.update()`, the frame loop, and drawing.

`logger.py` writes `game_state.jsonl` and `game_events.jsonl` for the boot.dev
result checker, and they are useful for reading a run back afterwards. Both are
gitignored. Logging is capped at about sixteen seconds of frames per run, and
the frame budget is restored at the start of each run -- so a second game played
without quitting logs as fully as the first.

## License

MIT
