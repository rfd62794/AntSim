# render.py — All drawing lives here; sim.py knows nothing about pygame.
import pygame
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    PHEROMONE_GRID_WIDTH, PHEROMONE_GRID_HEIGHT,
    CELL_W, CELL_H,
    NEST_RADIUS, FOOD_RADIUS,
    COL_BG, COL_NEST, COL_FOOD, COL_ANT, COL_ANT_FOOD,
    COL_PHEROMONE, COL_HUD,
)

# Pre-allocate a surface for the pheromone heatmap so we don't recreate it
# every frame (small but measurable saving at 4800 cells × per-pixel write).
_phero_surface: pygame.Surface | None = None
_cell_w_px = int(CELL_W)
_cell_h_px = int(CELL_H)


def render(screen: pygame.Surface, sim, clock: pygame.time.Clock):
    """Draw one complete frame onto *screen* and flip the display."""
    global _phero_surface

    # ── Background ────────────────────────────────────────────────────────────
    screen.fill(COL_BG)

    # ── Pheromone heatmap ────────────────────────────────────────────────────
    if _phero_surface is None:
        _phero_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

    _phero_surface.fill((0, 0, 0, 0))  # clear to transparent

    pr, pg, pb = COL_PHEROMONE
    for gy in range(PHEROMONE_GRID_HEIGHT):
        for gx in range(PHEROMONE_GRID_WIDTH):
            strength = sim.pheromone_grid[gy][gx]
            if strength <= 0:
                continue
            alpha   = int(strength / 255 * 180)          # max alpha 180
            px      = int(gx * CELL_W)
            py      = int(gy * CELL_H)
            _phero_surface.fill((pr, pg, pb, alpha),
                                rect=(px, py, _cell_w_px, _cell_h_px))

    screen.blit(_phero_surface, (0, 0))

    # ── Nest ──────────────────────────────────────────────────────────────────
    nx, ny = sim.nest_pos
    pygame.draw.circle(screen, COL_NEST, (nx, ny), NEST_RADIUS)
    pygame.draw.circle(screen, (255, 120, 100), (nx, ny), NEST_RADIUS, 3)  # rim

    # ── Food sources ──────────────────────────────────────────────────────────
    for fx, fy, _amount in sim.food_sources:
        pygame.draw.circle(screen, COL_FOOD, (int(fx), int(fy)), FOOD_RADIUS)
        pygame.draw.circle(screen, (150, 255, 160), (int(fx), int(fy)), FOOD_RADIUS, 2)

    # ── Ants ──────────────────────────────────────────────────────────────────
    for ant in sim.ants:
        colour = COL_ANT_FOOD if ant.carrying_food else COL_ANT
        px, py = int(ant.x), int(ant.y)
        pygame.draw.circle(screen, colour, (px, py), 4)
        # Energy bar (tiny, above the ant dot)
        bar_w  = 8
        bar_h  = 2
        filled = int(bar_w * (ant.energy / 100))
        pygame.draw.rect(screen, (80, 80, 80),  (px - bar_w // 2, py - 8, bar_w, bar_h))
        pygame.draw.rect(screen, (100, 220, 80), (px - bar_w // 2, py - 8, filled, bar_h))

    # ── HUD ───────────────────────────────────────────────────────────────────
    font = pygame.font.SysFont("consolas", 18)
    lines = [
        f"FPS:  {clock.get_fps():.1f}",
        f"Ants: {len(sim.ants)}",
        f"Food: {sim.food_collected}",
        f"Frame:{sim.frame}",
    ]
    for i, text in enumerate(lines):
        surf = font.render(text, True, COL_HUD)
        screen.blit(surf, (10, 10 + i * 22))

    # State legend (bottom-left)
    legend_font = pygame.font.SysFont("consolas", 14)
    legend = [
        ("wander",           (180, 180, 180)),
        ("follow pheromone", COL_PHEROMONE),
        ("seek food",        COL_FOOD),
        ("return nest",      COL_ANT_FOOD),
    ]
    for i, (label, col) in enumerate(legend):
        s = legend_font.render(f"■ {label}", True, col)
        screen.blit(s, (10, WINDOW_HEIGHT - 20 - i * 18))

    pygame.display.flip()
