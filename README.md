# Asteroids

A classic Asteroids arcade game built with Pygame. Course project for [boot.dev](https://www.boot.dev/).

## How to Play

```bash
uv sync
python3 main.py
```

### Modes

- **Classic** (default) -- survive as long as you can. The run ends when you
  lose all three lives.
- **Time trial** -- destroy 25 asteroids as fast as you can. The clock counts
  up, so a lower time is better. Losing all your lives ends the trial
  unfinished.

```bash
python3 main.py                                  # classic
python3 main.py --mode time-trial                # time trial, seed chosen for you
python3 main.py --mode time-trial --seed 1234    # replay a specific asteroid sequence
python3 main.py --seed 1234                      # classic on a fixed sequence
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

Destroy asteroids to survive. Large asteroids split into smaller ones when shot.
You lose a life when an asteroid hits your ship, and respawn in the middle with
a couple of seconds of invincibility.

### Seeds and best results

A seed fixes which asteroids arrive, from where, and how fast, so two runs of
the same seed face the same waves and their times and scores are worth
comparing. Spawning draws from a separate random stream to explosions and
splits, so how you play doesn't change what arrives next. Player input and
frame timing are still your own -- the seed reproduces the asteroid sequence,
not the whole run.

Best results are saved to `best_results.json` in the repo, keyed by mode and
seed: fastest time for a time trial, highest score for classic. Runs played
without a seed all share one "random" bucket. The file is gitignored, and is
separate from the logger's files described below.

## Development

```bash
uv run pytest        # Run tests
uv run ruff check .  # Lint
uv run ruff format . # Format
```

Tests in [`tests/`](tests/) cover the parts of the game that don't need a display:
screen wrapping and collision (`circleshape`), asteroid splitting, spawn geometry,
hull geometry and the shooting cooldown, particle lifetimes, seeded spawn
sequences (`rng`), the best-results store (`bestresults`), and the argument
parsing and run summaries in `main`. Keyboard handling in `Player.update()`, the
frame loop and drawing are deliberately untested -- they need an initialized
display.

`logger.py` writes `game_state.jsonl` and `game_events.jsonl` for the boot.dev
result checker. Both are gitignored.

## License

MIT
