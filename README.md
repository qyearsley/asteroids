# Asteroids

A classic Asteroids arcade game built with Pygame. Course project for [boot.dev](https://www.boot.dev/).

## How to Play

```bash
uv sync
python3 main.py
```

### Controls

- **W / S** -- thrust forward / backward
- **A / D** -- rotate left / right
- **Space** -- shoot

Destroy asteroids to survive. Large asteroids split into smaller ones when shot. Game ends when an asteroid hits your ship.

## Development

```bash
uv run pytest        # Run tests
uv run ruff check .  # Lint
uv run ruff format . # Format
```

Tests in [`tests/`](tests/) cover the parts of the game that don't need a display:
screen wrapping and collision (`circleshape`), asteroid splitting, spawn geometry,
hull geometry and the shooting cooldown, and particle lifetimes. Keyboard handling
in `Player.update()` is deliberately untested -- it needs an initialized display.

`logger.py` writes `game_state.jsonl` and `game_events.jsonl` for the boot.dev
result checker. Both are gitignored.

## License

MIT
