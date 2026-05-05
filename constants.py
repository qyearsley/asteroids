# Game window dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Player ship properties
PLAYER_RADIUS = 20
LINE_WIDTH = 2
PLAYER_TURN_SPEED = 300  # Degrees per second
PLAYER_SPEED = 200  # Pixels per second

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

# Scoring - more points for smaller (harder) asteroids
SCORE_PER_ASTEROID = {
    3: 20,   # Large asteroid (radius 60)
    2: 50,   # Medium asteroid (radius 40)
    1: 100,  # Small asteroid (radius 20)
}

# Lives
PLAYER_LIVES = 3
PLAYER_INVINCIBILITY_SECONDS = 2.0

# Particle effects
PARTICLE_COUNT = 8           # Number of particles per explosion
PARTICLE_SPEED_MIN = 50      # Minimum particle speed (pixels/sec)
PARTICLE_SPEED_MAX = 150     # Maximum particle speed (pixels/sec)
PARTICLE_LIFETIME = 0.6      # How long particles live (seconds)
PARTICLE_RADIUS = 2          # Size of each particle dot
