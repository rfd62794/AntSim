# constants.py — AntSim MVP
# All magic numbers live here. Change these to tune the simulation.

# ── Window ───────────────────────────────────────────────────────────────────
WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 600
FPS           = 60

# ── Nest / Food ───────────────────────────────────────────────────────────────
NEST_POS    = (400, 300)
NEST_RADIUS = 50
ANT_COUNT   = 10
FOOD_COUNT  = 5
FOOD_RADIUS = 20

# ── Ant ───────────────────────────────────────────────────────────────────────
ANT_SPEED          = 2.0
ANT_ENERGY_MAX     = 100.0
ANT_ENERGY_DRAIN   = 0.2   # 500 frames to die; ~300px round-trip at speed 2
ANT_RESPAWN_RATE   = 1     # new ant spawned at nest every N frames when colony < ANT_COUNT
ANT_VISION_RANGE   = 100
WANDER_TURN_MIN    = 20   # frames before next random direction change
WANDER_TURN_MAX    = 40

# ── Pheromone ─────────────────────────────────────────────────────────────────
PHEROMONE_DETECT_RANGE  = 40
PHEROMONE_EMIT          = 50
PHEROMONE_GRID_WIDTH    = 80
PHEROMONE_GRID_HEIGHT   = 60
PHEROMONE_DECAY         = 0.95
PHEROMONE_THRESHOLD     = 5

# Derived: pixel size of each grid cell
CELL_W = WINDOW_WIDTH  / PHEROMONE_GRID_WIDTH   # 10 px
CELL_H = WINDOW_HEIGHT / PHEROMONE_GRID_HEIGHT  # 10 px

# ── Colours ───────────────────────────────────────────────────────────────────
COL_BG         = (10,  12,  20)
COL_NEST       = (200, 60,  40)
COL_FOOD       = (60,  200, 80)
COL_ANT        = (240, 220, 180)   # cream / tan
COL_ANT_FOOD   = (255, 180, 40)    # orange when carrying food
COL_PHEROMONE  = (60,  120, 255)   # blue heatmap
COL_HUD        = (200, 200, 200)
