# sim.py — Simulation state and update logic
import math
import random
from ant import Ant
from queen import Queen
from constants import (
    ANT_COUNT, ANT_COUNT_MAX,
    FOOD_COUNT, FOOD_RADIUS, NEST_POS, NEST_RADIUS,
    ANT_ENERGY_MAX,
    QUEEN_REPRO_COST, QUEEN_REPRO_INTERVAL,
    PHEROMONE_GRID_WIDTH, PHEROMONE_GRID_HEIGHT,
    PHEROMONE_DECAY, PHEROMONE_THRESHOLD,
    WINDOW_WIDTH, WINDOW_HEIGHT,
    CELL_W, CELL_H,
)

# Minimum distance a food source must be from the nest
_FOOD_SPAWN_MIN_DIST = 100


def _spawn_food_sources(n: int) -> list:
    """Generate n food sources at random positions, away from the nest."""
    sources = []
    nx, ny  = NEST_POS
    while len(sources) < n:
        x = random.randint(FOOD_RADIUS + 5, WINDOW_WIDTH  - FOOD_RADIUS - 5)
        y = random.randint(FOOD_RADIUS + 5, WINDOW_HEIGHT - FOOD_RADIUS - 5)
        if math.hypot(x - nx, y - ny) >= _FOOD_SPAWN_MIN_DIST:
            sources.append([x, y, 100])   # [x, y, amount]
    return sources


class Simulation:
    """Owns all simulation state.  Call update() once per frame."""

    def __init__(self):
        self.nest_pos    = NEST_POS
        self.queen       = Queen(*NEST_POS)
        self.food_sources = _spawn_food_sources(FOOD_COUNT)

        # 2-D list [row][col] of pheromone strengths (0-255)
        self.pheromone_grid = [[0.0] * PHEROMONE_GRID_WIDTH
                               for _ in range(PHEROMONE_GRID_HEIGHT)]

        self.food_collected = 0
        self.food_storage   = 0   # food units banked in the nest (fuels reproduction)
        self.frame          = 0

        # Spawn initial worker cohort — inherit Queen's base genes directly
        self.ants = [
            Ant(*NEST_POS, genes=dict(self.queen.genes), queen_id=id(self.queen))
            for _ in range(ANT_COUNT)
        ]

    # ──────────────────────────────────────────────────────────────────────────
    # Public
    # ──────────────────────────────────────────────────────────────────────────

    def update(self):
        self.frame += 1

        # 1. Update ants (movement + state)
        for ant in self.ants:
            if ant.is_alive():
                ant.update(self.food_sources, self.nest_pos, self.pheromone_grid)

        # 2. Collisions: food pickup
        self._check_food_pickup()

        # 3. Collisions: nest drop-off (also increments food_storage)
        self._check_nest_dropoff()

        # 4. Emit pheromone — only food-carrying ants lay trail (canonical ACO)
        for ant in self.ants:
            if ant.is_alive() and ant.carrying_food:
                ant.emit_pheromone(self.pheromone_grid)

        # 5. Decay pheromone grid
        self._decay_pheromone()

        # 6. Remove dead ants
        self.ants = [a for a in self.ants if a.is_alive()]

        # 7. Queen reproduction (checked every QUEEN_REPRO_INTERVAL frames)
        if self.queen.alive and self.frame % QUEEN_REPRO_INTERVAL == 0:
            if len(self.ants) < ANT_COUNT_MAX:
                new_worker = self.queen.try_reproduce(self.food_storage)
                if new_worker is not None:
                    self.ants.append(new_worker)
                    self.food_storage -= QUEEN_REPRO_COST

        # 8. Respawn food if all gone
        if not self.food_sources:
            self.food_sources = _spawn_food_sources(FOOD_COUNT)

    def get_pheromone_strength(self, x: float, y: float) -> float:
        """Return pheromone strength at pixel coordinate (x, y)."""
        gx = max(0, min(PHEROMONE_GRID_WIDTH  - 1, int(x / CELL_W)))
        gy = max(0, min(PHEROMONE_GRID_HEIGHT - 1, int(y / CELL_H)))
        return self.pheromone_grid[gy][gx]

    # ──────────────────────────────────────────────────────────────────────────
    # Internal
    # ──────────────────────────────────────────────────────────────────────────

    def _check_food_pickup(self):
        """Ants not carrying food that touch a food source pick it up."""
        for ant in self.ants:
            if ant.carrying_food or not ant.is_alive():
                continue
            for source in self.food_sources:
                fx, fy, amount = source
                if amount <= 0:
                    continue
                if math.hypot(ant.x - fx, ant.y - fy) <= FOOD_RADIUS:
                    ant.carrying_food = True
                    source[2] -= 1
                    break
        # Prune exhausted food sources
        self.food_sources = [s for s in self.food_sources if s[2] > 0]

    def _check_nest_dropoff(self):
        """Ants carrying food that touch the nest deposit to food_storage."""
        nx, ny = self.nest_pos
        for ant in self.ants:
            if not ant.carrying_food or not ant.is_alive():
                continue
            if math.hypot(ant.x - nx, ant.y - ny) <= NEST_RADIUS:
                ant.carrying_food = False
                ant.energy        = ANT_ENERGY_MAX   # reset energy on return
                self.food_collected += 1
                self.food_storage   += 1             # bank food for Queen

    def _decay_pheromone(self):
        """Multiply every cell by decay factor; zero out cells below threshold."""
        for row in self.pheromone_grid:
            for i in range(len(row)):
                v = row[i] * PHEROMONE_DECAY
                row[i] = v if v >= PHEROMONE_THRESHOLD else 0.0
