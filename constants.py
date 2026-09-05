# Game window dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Player ship properties
PLAYER_RADIUS = 20
LINE_WIDTH = 2
PLAYER_TURN_SPEED = 300  # Degrees per second
PLAYER_SPEED = 200  # Pixels per second
# Half the hull's width, as a fraction of its radius. Below 1 makes the ship
# longer than it is wide, which is what makes it read as pointing somewhere.
HULL_WIDTH_RATIO = 1 / 1.5

# Asteroid properties
ASTEROID_MIN_RADIUS = 20
ASTEROID_KINDS = 3  # Number of different asteroid sizes
ASTEROID_SPAWN_RATE_SECONDS = 0.8  # Time between new asteroid spawns
ASTEROID_MAX_RADIUS = ASTEROID_MIN_RADIUS * ASTEROID_KINDS  # Largest asteroid size
ASTEROID_SPLIT_ANGLE_MIN = 20  # Minimum random split angle (degrees)
ASTEROID_SPLIT_ANGLE_MAX = 50  # Maximum random split angle (degrees)
ASTEROID_SPLIT_SPEED_MULTIPLIER = 1.2  # Speed boost when splitting

# Bullet properties
SHOT_RADIUS = 5
PLAYER_SHOOT_SPEED = 500
PLAYER_SHOOT_COOLDOWN_SECONDS = 0.3
# How long a bullet lives before it fades. Bullets used to have no lifetime at
# all: they wrapped at the screen edge and flew until they hit something, so at
# one shot every 0.3s a run accumulated permanent sprites for as long as it
# lasted, and holding fire cleared the field by attrition. This is the single
# number that decides how far a shot reaches -- 1.6s at 500px/s is about 800
# pixels, roughly two thirds of the screen, which is the classic arcade range.
SHOT_LIFETIME_SECONDS = 1.6

# Difficulty ramp. The spawn interval starts at ASTEROID_SPAWN_RATE_SECONDS and
# shortens towards ASTEROID_SPAWN_RATE_FLOOR over ASTEROID_RAMP_SECONDS, after
# which it stays there. Without it minute ten of a classic run was identical to
# minute one -- the only thing that grew was the count already on screen, so the
# game got harder by clutter rather than by pressure.
ASTEROID_SPAWN_RATE_FLOOR = 0.3
ASTEROID_RAMP_SECONDS = 180.0

# Scoring - more points for smaller (harder) asteroids
SCORE_PER_ASTEROID = {
    3: 20,  # Large asteroid (radius 60)
    2: 50,  # Medium asteroid (radius 40)
    1: 100,  # Small asteroid (radius 20)
}
# What an asteroid whose radius is not a clean multiple of the minimum is worth.
# Nothing produces one today -- `split` subtracts exactly one minimum radius --
# but the lookup needs a fallback, and a bare literal at the call site read as a
# magic number that only happened to match the largest size.
SCORE_FOR_ODD_ASTEROID = SCORE_PER_ASTEROID[ASTEROID_KINDS]

# Lives
PLAYER_LIVES = 3
PLAYER_INVINCIBILITY_SECONDS = 2.0

# Game modes
MODE_CLASSIC = "classic"  # Play until you run out of lives
MODE_TIME_TRIAL = "time-trial"  # Destroy a set number of asteroids as fast as possible
TIME_TRIAL_TARGET_ASTEROIDS = 25  # How many to destroy to finish a time trial

# Local best results, kept apart from the logger's jsonl files
BEST_RESULTS_FILE = "best_results.json"

# Text layout
TEXT_LINE_HEIGHT = 40  # Vertical spacing between lines on the menu screens

# Particle effects
PARTICLE_COUNT = 8  # Number of particles per explosion
PARTICLE_SPEED_MIN = 50  # Minimum particle speed (pixels/sec)
PARTICLE_SPEED_MAX = 150  # Maximum particle speed (pixels/sec)
PARTICLE_LIFETIME = 0.6  # How long particles live (seconds)
PARTICLE_RADIUS = 2  # Size of each particle dot
