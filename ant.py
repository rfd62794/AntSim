# ant.py — Ant agent with a 4-state FSM + gene-driven behaviour
import math
import random
from constants import (
    ANT_SPEED, ANT_ENERGY_MAX, ANT_ENERGY_DRAIN, ANT_ENERGY_GAIN,
    ANT_VISION_RANGE, PHEROMONE_DETECT_RANGE,
    PHEROMONE_EMIT_STRONG, PHEROMONE_EMIT_WEAK, PHEROMONE_THRESHOLD,
    WINDOW_WIDTH, WINDOW_HEIGHT,
    WANDER_TURN_MIN, WANDER_TURN_MAX,
    NEST_RADIUS, FOOD_RADIUS,
    CELL_W, CELL_H,
    PHEROMONE_GRID_WIDTH, PHEROMONE_GRID_HEIGHT,
)

# Default genes for ants created without a Queen (e.g., headless tests)
_DEFAULT_GENES = {
    'sensitivity':       1.0,
    'speed':             1.0,
    'boldness':          0.5,
    'lifespan':          1.0,
    'energy_efficiency': 1.0,
}


def _angle_to_vec(angle: float):
    """Convert a radian angle to a unit (dx, dy) vector."""
    return math.cos(angle), math.sin(angle)


class Ant:
    """
    Single ant agent.

    Genes (all multiplicative scalars, range 0.5–1.5):
      sensitivity  — scales pheromone detect range
      speed        — scales movement px/frame
      boldness     — [0,1] chance to keep wandering instead of following trail
    """

    def __init__(self, x: float, y: float,
                 genes: dict | None = None,
                 queen_id: int | None = None):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.tau)
        self.vx, self.vy  = _angle_to_vec(angle)
        self.carrying_food = False
        self.state         = "wander"
        self.queen_id      = queen_id           # lineage tracking
        self._wander_timer = random.randint(WANDER_TURN_MIN, WANDER_TURN_MAX)
        self._wander_angle = angle

        # Genes — copy so mutations don't alias the Queen's dict
        self.genes = dict(genes) if genes is not None else dict(_DEFAULT_GENES)

        # Derived per-ant constants (computed once at birth)
        self.max_energy         = ANT_ENERGY_MAX * self.genes['lifespan']
        self.energy: float      = self.max_energy
        self.energy_drain_rate  = ANT_ENERGY_DRAIN / self.genes['energy_efficiency']
        self.actual_speed       = ANT_SPEED          * self.genes['speed']
        self.phero_detect_range = PHEROMONE_DETECT_RANGE * self.genes['sensitivity']
        self.vision_range       = ANT_VISION_RANGE   * self.genes['sensitivity']

    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────

    def update(self, food_sources: list, nest_pos: tuple, pheromone_grid: list):
        """Advance the ant one simulation frame."""
        if not self.is_alive():
            return

        # ── State Transitions ────────────────────────────────────────────────
        if self.carrying_food:
            self.state = "return_nest"
        elif self.energy < self.max_energy * 0.3:
            # Low energy: prioritize return to nest
            self.state = "return_nest"
        else:
            # We sample from the location locally via grid lookup, which is abstracted in _sample_pheromone.
            phero_dir = self._sample_pheromone(pheromone_grid)
            food_dir  = self._nearest_food_dir(food_sources)

            if food_dir is not None:
                self.state = "seek_food"
            elif phero_dir is not None:
                # Use current position cell strength
                my_gx = int(self.x / CELL_W)
                my_gy = int(self.y / CELL_H)
                my_gx = max(0, min(PHEROMONE_GRID_WIDTH  - 1, my_gx))
                my_gy = max(0, min(PHEROMONE_GRID_HEIGHT - 1, my_gy))
                phero_strength = pheromone_grid[my_gy][my_gx]

                # HIGH sensitivity ants follow trails more strictly (only follow strong trails > 50)
                if phero_strength > 50 * self.genes['sensitivity']:
                    self.state = "follow_pheromone"
                elif phero_strength > 20:
                    if random.random() < self.genes['sensitivity'] and random.random() >= self.genes['boldness']:
                        self.state = "follow_pheromone"
                    else:
                        self.state = "wander"
                else:
                    self.state = "wander"
            else:
                self.state = "wander"

        # ── Movement ─────────────────────────────────────────────────────────
        if self.state == "wander":
            self._do_wander()
        elif self.state == "follow_pheromone":
            dx, dy = self._sample_pheromone(pheromone_grid)
            self._steer(dx, dy)
        elif self.state == "seek_food":
            dx, dy = self._nearest_food_dir(food_sources)
            self._steer(dx, dy)
        elif self.state == "return_nest":
            nx, ny = nest_pos
            dx, dy = nx - self.x, ny - self.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                self._steer(dx / dist, dy / dist)

        # Apply velocity — speed scaled by gene
        self.x += self.vx * self.actual_speed
        self.y += self.vy * self.actual_speed
        self._clamp_to_bounds()

        # ── Energy ───────────────────────────────────────────────────────────
        self.energy -= self.energy_drain_rate
        if self.carrying_food:
            self.energy = min(self.max_energy, self.energy + ANT_ENERGY_GAIN)

    def emit_pheromone(self, pheromone_grid: list):
        """Add pheromone at the ant's current grid cell."""
        if self.carrying_food and self.state == "return_nest":
            emit_str = PHEROMONE_EMIT_STRONG
        else:
            emit_str = PHEROMONE_EMIT_WEAK

        gx = int(self.x / CELL_W)
        gy = int(self.y / CELL_H)
        gx = max(0, min(PHEROMONE_GRID_WIDTH  - 1, gx))
        gy = max(0, min(PHEROMONE_GRID_HEIGHT - 1, gy))
        pheromone_grid[gy][gx] = min(255, pheromone_grid[gy][gx] + emit_str)

    def is_alive(self) -> bool:
        return self.energy > 0

    # ──────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _do_wander(self):
        """Random walk: nudge direction every N frames."""
        self._wander_timer -= 1
        if self._wander_timer <= 0:
            self._wander_angle += random.uniform(-math.pi / 2, math.pi / 2)
            self._wander_timer  = random.randint(WANDER_TURN_MIN, WANDER_TURN_MAX)
        self.vx, self.vy = _angle_to_vec(self._wander_angle)

    def _steer(self, dx: float, dy: float):
        """Gently blend velocity toward (dx, dy) direction."""
        length = math.hypot(dx, dy)
        if length < 1e-6:
            return
        tx, ty = dx / length, dy / length
        # Lerp: 70 % new direction, 30 % old momentum → smooth turning
        self.vx = 0.3 * self.vx + 0.7 * tx
        self.vy = 0.3 * self.vy + 0.7 * ty
        norm = math.hypot(self.vx, self.vy)
        if norm > 1e-6:
            self.vx /= norm
            self.vy /= norm

    def _clamp_to_bounds(self):
        """Bounce off window edges."""
        if self.x < 0:
            self.x = 0
            self.vx = abs(self.vx)
            self._wander_angle = math.atan2(self.vy, self.vx)
        elif self.x > WINDOW_WIDTH:
            self.x = WINDOW_WIDTH
            self.vx = -abs(self.vx)
            self._wander_angle = math.atan2(self.vy, self.vx)
        if self.y < 0:
            self.y = 0
            self.vy = abs(self.vy)
            self._wander_angle = math.atan2(self.vy, self.vx)
        elif self.y > WINDOW_HEIGHT:
            self.y = WINDOW_HEIGHT
            self.vy = -abs(self.vy)
            self._wander_angle = math.atan2(self.vy, self.vx)

    def _sample_pheromone(self, pheromone_grid: list):
        """
        Look at grid cells within phero_detect_range (gene-scaled).
        Return (dx, dy) toward the strongest cell, or None.
        """
        best_val  = PHEROMONE_THRESHOLD
        best_dx   = None
        best_dy   = None
        radius_cells_x = int(self.phero_detect_range / CELL_W) + 1
        radius_cells_y = int(self.phero_detect_range / CELL_H) + 1
        my_gx = int(self.x / CELL_W)
        my_gy = int(self.y / CELL_H)
        for gy in range(max(0, my_gy - radius_cells_y),
                         min(PHEROMONE_GRID_HEIGHT, my_gy + radius_cells_y + 1)):
            for gx in range(max(0, my_gx - radius_cells_x),
                             min(PHEROMONE_GRID_WIDTH, my_gx + radius_cells_x + 1)):
                val = pheromone_grid[gy][gx]
                if val <= best_val:
                    continue
                cx = (gx + 0.5) * CELL_W
                cy = (gy + 0.5) * CELL_H
                dx, dy = cx - self.x, cy - self.y
                dist = math.hypot(dx, dy)
                if dist <= self.phero_detect_range:
                    best_val = val
                    best_dx  = dx
                    best_dy  = dy
        if best_dx is not None:
            return best_dx, best_dy
        return None

    def _nearest_food_dir(self, food_sources: list):
        """
        Scan food sources within vision_range (gene-scaled).
        Return (dx, dy) toward the closest one, or None.
        """
        best_dist = self.vision_range
        best_dx   = None
        best_dy   = None
        for node in food_sources:
            if node.is_depleted():
                continue
            dx, dy = node.x - self.x, node.y - self.y
            dist = math.hypot(dx, dy)
            if dist < best_dist:
                best_dist = dist
                best_dx   = dx
                best_dy   = dy
        if best_dx is not None:
            return best_dx, best_dy
        return None
