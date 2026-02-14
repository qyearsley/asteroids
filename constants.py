# Game window dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Player ship properties
PLAYER_RADIUS = 20
LINE_WIDTH = 2
PLAYER_TURN_SPEED = 300  # Degrees per second
PLAYER_SPEED = 200       # Pixels per second

# Asteroid properties
ASTEROID_MIN_RADIUS = 20
ASTEROID_KINDS = 3                 # Number of different asteroid sizes
ASTEROID_SPAWN_RATE_SECONDS = 0.8  # Time between new asteroid spawns
ASTEROID_MAX_RADIUS = ASTEROID_MIN_RADIUS * ASTEROID_KINDS  # Largest asteroid size
