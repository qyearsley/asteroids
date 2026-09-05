#!/usr/bin/env python3
import argparse
from enum import Enum, auto

import pygame

import asteroid
import asteroidfield
import bestresults
import constants
import logger
import particle
import player
import rng
import shot


class State(Enum):
    """Which screen the game is showing. `main()` moves between these."""

    TITLE = auto()
    PLAYING = auto()
    GAME_OVER = auto()
    QUIT = auto()


def parse_args(argv=None):
    """Read the command line. Split out from `main()` so it can be tested."""
    target = constants.TIME_TRIAL_TARGET_ASTEROIDS
    parser = argparse.ArgumentParser(description="Classic Asteroids arcade game.")
    parser.add_argument(
        "--mode",
        choices=[constants.MODE_CLASSIC, constants.MODE_TIME_TRIAL],
        default=constants.MODE_CLASSIC,
        help=(
            f"'{constants.MODE_CLASSIC}' plays until you run out of lives; "
            f"'{constants.MODE_TIME_TRIAL}' asks you to destroy {target} asteroids "
            "as fast as you can (default: %(default)s)"
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        help=(
            "seed the asteroid sequence so the same run can be replayed and compared. "
            "Time trials pick a seed for you if you leave this out"
        ),
    )
    return parser.parse_args(argv)


def setup_display():
    """Open the window and return the pieces every screen needs."""
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    pygame.init()
    screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
    pygame.display.set_caption("Asteroids")
    print(f"Screen width: {constants.SCREEN_WIDTH}")
    print(f"Screen height: {constants.SCREEN_HEIGHT}")

    # Clock controls frame rate.
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    return screen, clock, font


def draw_centred_lines(screen, font, lines):
    """Draw a block of centred text, one line under the next."""
    height = len(lines) * constants.TEXT_LINE_HEIGHT
    top = constants.SCREEN_HEIGHT // 2 - height // 2
    for i, line in enumerate(lines):
        surface = font.render(line, True, "white")
        centre = (constants.SCREEN_WIDTH // 2, top + i * constants.TEXT_LINE_HEIGHT)
        screen.blit(surface, surface.get_rect(center=centre))


def format_time(seconds):
    """Seconds as `M:SS.hh`, which reads better than a raw float on the timer."""
    minutes, seconds = divmod(seconds, 60)
    return f"{int(minutes)}:{seconds:05.2f}"


def make_result(mode, seed, score, destroyed, elapsed):
    """A summary of one finished run, also the shape stored in the bests file."""
    return {
        "mode": mode,
        "seed": seed,
        "score": score,
        "time": round(elapsed, 2),
        "asteroids": destroyed,
        # Only a time trial has something to complete; classic ends when you die.
        "completed": mode == constants.MODE_TIME_TRIAL
        and destroyed >= constants.TIME_TRIAL_TARGET_ASTEROIDS,
    }


def best_line(mode, best):
    """One line describing a stored best, or None if there isn't one yet."""
    if best is None:
        return None
    if mode == constants.MODE_TIME_TRIAL:
        return f"Best time for this seed: {format_time(best['time'])}"
    return f"Best score: {best['score']}"


def title_lines(mode, seed, best):
    """The text of the title screen."""
    lines = ["ASTEROIDS", ""]
    if mode == constants.MODE_TIME_TRIAL:
        lines.append(f"Time trial: destroy {constants.TIME_TRIAL_TARGET_ASTEROIDS} asteroids")
        lines.append("as fast as you can")
    else:
        lines.append("Classic: survive as long as you can")
    if seed is not None:
        lines.append(f"Seed: {seed}")
    stored = best_line(mode, best)
    if stored is not None:
        lines.append(stored)
    lines += [
        "",
        "W and S to thrust, A and D to turn, Space to shoot",
        "P to pause, Escape to end the run",
        "",
        "Press Enter to play, or Q to quit",
    ]
    return lines


def result_lines(result, best, improved):
    """The text of the game over screen."""
    if result["mode"] == constants.MODE_TIME_TRIAL:
        target = constants.TIME_TRIAL_TARGET_ASTEROIDS
        if result["completed"]:
            lines = ["Time trial finished!", f"Time: {format_time(result['time'])}"]
        else:
            lines = [
                "Out of lives -- time trial not finished",
                f"You destroyed {result['asteroids']} of {target} asteroids",
                f"Time: {format_time(result['time'])}",
            ]
        lines.append(f"Seed: {result['seed']}")
    else:
        lines = ["Game over", f"Time survived: {format_time(result['time'])}"]
        if result["seed"] is not None:
            lines.append(f"Seed: {result['seed']}")
    lines.append(f"Score: {result['score']}")

    if improved:
        lines.append("New best!")
    else:
        stored = best_line(result["mode"], best)
        if stored is not None:
            lines.append(stored)

    lines += ["", "Press R to play again, or Q to quit"]
    return lines


def wait_for_choice(screen, clock, font, lines, start_key):
    """Show a static screen until the player starts a run, quits, or closes the window."""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return State.QUIT
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    return State.QUIT
                if event.key == start_key:
                    return State.PLAYING

        screen.fill("black")
        draw_centred_lines(screen, font, lines)
        pygame.display.flip()
        clock.tick(60)


def draw_hud(screen, font, mode, score, lives, destroyed, elapsed):
    """Score and lives in the top left, plus the trial timer when one is running."""
    lines = [f"Score: {score}", f"Lives: {lives}"]
    if mode == constants.MODE_TIME_TRIAL:
        lines.append(f"Time: {format_time(elapsed)}")
        lines.append(f"Asteroids: {destroyed} / {constants.TIME_TRIAL_TARGET_ASTEROIDS}")
    for i, line in enumerate(lines):
        screen.blit(font.render(line, True, "white"), (10, 10 + i * constants.HUD_LINE_HEIGHT))


def resolve_collisions(p, asteroids, shots):
    """Settle one frame of ship-and-bullet collisions, and say what it cost.

    Split out of the main loop so it can be tested: it needs no display, and it
    is where the scoring actually happens. Everything it changes it changes
    through the sprites themselves -- killing shots, splitting asteroids,
    respawning the ship -- so the caller only has to add up what comes back.

    Args:
        p: The player.
        asteroids: The asteroid group.
        shots: The bullet group.

    Returns:
        `(hits, points, destroyed)` -- lives lost, score earned, and asteroids
        broken this frame.
    """
    hits = 0
    points = 0
    destroyed = 0
    for x in asteroids:
        if p.invincibility_timer <= 0 and x.collides_with(p):
            logger.log_event("player_hit")
            hits += 1
            p.respawn()
        for s in shots:
            if x.collides_with(s):
                logger.log_event("asteroid_shot")
                kind = int(x.radius / constants.ASTEROID_MIN_RADIUS)
                points += constants.SCORE_PER_ASTEROID.get(kind, constants.SCORE_FOR_ODD_ASTEROID)
                destroyed += 1
                particle.spawn_explosion(x.position.x, x.position.y)
                x.split()
                s.kill()
                # `x` is dead now. Without this the loop kept testing the
                # remaining shots against it, so two shots landing on one
                # asteroid in the same frame scored it twice, split it twice --
                # four children instead of two -- and drew two explosions.
                break
    return hits, points, destroyed


def play_run(screen, clock, font, mode, seed):
    """Play one run from a clean slate and return `(result, next_state)`.

    Every group and object a run needs is created here, so calling this again
    starts a genuinely fresh game -- no asteroids or particles left over from
    the last one, and the same seed replays the same asteroid sequence.
    """
    rng.reseed(seed)

    # Create sprite groups for game object management
    updatable = pygame.sprite.Group()  # Objects that need update() called
    drawable = pygame.sprite.Group()  # Objects that need draw() called
    asteroids = pygame.sprite.Group()  # Asteroids for collision detection
    shots = pygame.sprite.Group()

    # Assign sprite groups as class-level containers
    # Objects will auto-add themselves to these groups on instantiation
    asteroid.Asteroid.containers = (asteroids, updatable, drawable)
    player.Player.containers = (updatable, drawable)
    shot.Shot.containers = (shots, updatable, drawable)
    particle.Particle.containers = (updatable, drawable)
    asteroidfield.AsteroidField.containers = (updatable,)

    p = player.Player(constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2)
    asteroidfield.AsteroidField()

    score = 0
    lives = constants.PLAYER_LIVES
    destroyed = 0
    elapsed = 0.0  # Seconds of play, not counting time spent paused
    paused = False

    logger.start_run()

    dt = 0  # Delta time in seconds
    while True:
        # Named explicitly rather than harvested from this function's locals.
        # The logger used to read them through `inspect`, which quietly made
        # every local name in here part of its interface.
        logger.log_state(
            {
                "updatable": updatable,
                "drawable": drawable,
                "asteroids": asteroids,
                "shots": shots,
            },
            screen,
        )

        # Handle quit, pause and give-up events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return make_result(mode, seed, score, destroyed, elapsed), State.QUIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_ESCAPE:
                    # End the run early rather than killing the whole process.
                    return make_result(mode, seed, score, destroyed, elapsed), State.GAME_OVER

        # Clear screen.
        screen.fill("black")

        if not paused:
            elapsed += dt

            # Update all game objects.
            for x in updatable:
                x.update(dt)

            hits, points, smashed = resolve_collisions(p, asteroids, shots)
            lives -= hits
            score += points
            destroyed += smashed

            # The run is over once the lives are gone, or the trial target is met.
            result = make_result(mode, seed, score, destroyed, elapsed)
            if lives <= 0 or result["completed"]:
                print("Game over!")
                return result, State.GAME_OVER

        # Draw all game objects.
        for x in drawable:
            x.draw(screen)

        draw_hud(screen, font, mode, score, lives, destroyed, elapsed)
        if paused:
            draw_centred_lines(screen, font, ["Paused", "Press P to carry on"])

        # Update display and calculate delta time.
        pygame.display.flip()
        dt = clock.tick(60) / 1000  # Limit to 60 FPS, convert ms to seconds


def main(argv=None):
    """Set the game up once, then move between the title, play and game over screens."""
    args = parse_args(argv)
    mode = args.mode
    seed = args.seed
    # A trial needs a seed to be worth comparing, so pick one if the player didn't.
    if mode == constants.MODE_TIME_TRIAL and seed is None:
        seed = rng.random_seed()
        print(f"Time trial seed: {seed}")

    screen, clock, font = setup_display()

    state = State.TITLE
    result = None
    best = bestresults.best_for(bestresults.load(), mode, seed)
    improved = False

    while state is not State.QUIT:
        if state is State.TITLE:
            state = wait_for_choice(
                screen, clock, font, title_lines(mode, seed, best), pygame.K_RETURN
            )
        elif state is State.PLAYING:
            result, state = play_run(screen, clock, font, mode, seed)
            # Recorded however the run ended, closing the window included. It
            # used to be recorded only on GAME_OVER, so a personal best set in a
            # run you then quit out of was simply thrown away.
            improved, best = bestresults.record(mode, seed, result)
        elif state is State.GAME_OVER:
            state = wait_for_choice(
                screen, clock, font, result_lines(result, best, improved), pygame.K_r
            )
            if state is State.PLAYING and improved:
                # The record we just set is now the one to beat.
                best = result
                improved = False

    pygame.quit()


if __name__ == "__main__":
    main()
