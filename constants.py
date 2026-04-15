# constants.py — AntSim MVP
# All magic numbers live here. Change these to tune the simulation.

# ── Window ───────────────────────────────────────────────────────────────────
WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 600
FPS           = 60

# ── Nest / Food ───────────────────────────────────────────────────────────────
NEST_POS    = (400, 300)
NEST_RADIUS = 50
ANT_COUNT   = 10          # initial worker cohort size
ANT_COUNT_MAX = 40        # hard ceiling on colony size
FOOD_COUNT  = 5
FOOD_RADIUS = 20

# ── Queen ─────────────────────────────────────────────────────────────────────
QUEEN_ENERGY_MAX      = 200.0
QUEEN_REPRO_COST      = 20    # food_storage units consumed per new worker
QUEEN_REPRO_INTERVAL  = 60    # frames between reproduction checks (1 s at 60 FPS)
GENE_MUTATION_CHANCE  = 0.05  # 5 % per gene per birth
GENE_MUTATION_RANGE   = 0.05  # ±5 % shift when mutation fires
GENE_MIN              = 0.5
GENE_MAX              = 1.5

# ── Ant ───────────────────────────────────────────────────────────────────────
ANT_SPEED          = 2.0   # base px/frame; multiplied by genes['speed']
ANT_ENERGY_MAX     = 100.0
ANT_ENERGY_DRAIN   = 0.2   # 500 frames to die; ~300px round-trip at base speed
ANT_VISION_RANGE   = 100   # base px; multiplied by genes['sensitivity']
WANDER_TURN_MIN    = 20    # frames before next random direction change
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
COL_QUEEN      = (255, 80,  200)   # magenta — distinct from nest red
