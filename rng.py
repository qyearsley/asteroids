"""Random numbers for one run of the game.

The game draws from the generators here instead of calling the module-level
`random` functions, so seeding a run makes it repeatable. There are two
separate streams: how many explosions or splits a player triggers then has no
effect on which asteroids arrive next, which is what makes two runs on the same
seed comparable.
"""

import random

# Asteroid arrivals -- the part of a run that has to match between two runs for
# their times and scores to mean the same thing.
spawns = random.Random()
# Cosmetic and derived randomness: split angles and explosion particles.
effects = random.Random()


def reseed(seed=None):
    """Start fresh generators for a run. `None` means unpredictable, as in normal play."""
    global spawns, effects
    spawns = random.Random(seed)
    # Offset the second stream so it isn't a copy of the first.
    effects = random.Random(None if seed is None else seed + 1)


def random_seed():
    """Pick a seed for the player, small enough to write down and retype."""
    return random.randrange(1_000_000)
