# ant.py — Ant agent with a 4-state FSM
import math
import random
from constants import (
    ANT_SPEED, ANT_ENERGY_MAX, ANT_ENERGY_DRAIN,
    ANT_VISION_RANGE, PHEROMONE_DETECT_RANGE,
    PHEROMONE_EMIT, PHEROMONE_THRESHOLD,
    WINDOW_WIDTH, WINDOW_HEIGHT,
    WANDER_TURN_MIN, WANDER_TURN_MAX,
    NEST_RADIUS, FOOD_RADIUS,
    CELL_W, CELL_H,
    PHEROMONE_GRID_WIDTH, PHEROMONE_GRID_HEIGHT,
)


def _angle_to_vec(angle: float):
    """Convert a radian angle to a unit (dx, dy) vector."""
    return math.cos(angle), math.sin(angle)


class Ant:
    """Single ant agent.  States: wander | follow_pheromone | seek_food | return_nest"""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.tau)
        self.vx, self.vy = _angle_to_vec(angle)
        self.energy: float   = ANT_ENERGY_MAX
        self.carrying_food   = False
        self.state           = "wander"
        self._wander_timer   = random.randint(WANDER_TURN_MIN, WANDER_TURN_MAX)
        self._wander_angle   = angle

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
        else:
            phero_dir = self._sample_pheromone(pheromone_grid)
            food_dir  = self._nearest_food_dir(food_sources)
            if phero_dir is not None:
                self.state = "follow_pheromone"
            elif food_dir is not None:
                self.state = "seek_food"
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

        # Apply velocity
        self.x += self.vx * ANT_SPEED
        self.y += self.vy * ANT_SPEED
        self._clamp_to_bounds()

        # ── Energy ───────────────────────────────────────────────────────────
        self.energy -= ANT_ENERGY_DRAIN

    def emit_pheromone(self, pheromone_grid: list):
        """Add pheromone at the ant's current grid cell."""
        gx = int(self.x / CELL_W)
        gy = int(self.y / CELL_H)
        gx = max(0, min(PHEROMONE_GRID_WIDTH  - 1, gx))
        gy = max(0, min(PHEROMONE_GRID_HEIGHT - 1, gy))
        pheromone_grid[gy][gx] = min(255, pheromone_grid[gy][gx] + PHEROMONE_EMIT)

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
        Look at grid cells within PHEROMONE_DETECT_RANGE.
        Return (dx, dy) unit vector toward strongest cell, or None.
        """
        best_val  = PHEROMONE_THRESHOLD
        best_dx   = None
        best_dy   = None
        # Grid search window in cell units
        radius_cells_x = int(PHEROMONE_DETECT_RANGE / CELL_W) + 1
        radius_cells_y = int(PHEROMONE_DETECT_RANGE / CELL_H) + 1
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
                if dist <= PHEROMONE_DETECT_RANGE:
                    best_val = val
                    best_dx  = dx
                    best_dy  = dy
        if best_dx is not None:
            return best_dx, best_dy
        return None

    def _nearest_food_dir(self, food_sources: list):
        """
        Scan food sources within ANT_VISION_RANGE.
        Return (dx, dy) toward closest one, or None.
        """
        best_dist = ANT_VISION_RANGE
        best_dx   = None
        best_dy   = None
        for (fx, fy, _amount) in food_sources:
            dx, dy = fx - self.x, fy - self.y
            dist = math.hypot(dx, dy)
            if dist < best_dist:
                best_dist = dist
                best_dx   = dx
                best_dy   = dy
        if best_dx is not None:
            return best_dx, best_dy
        return None
