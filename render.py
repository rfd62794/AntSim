# render.py — All drawing lives here; sim.py knows nothing about pygame.
import pygame
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    PHEROMONE_GRID_WIDTH, PHEROMONE_GRID_HEIGHT,
    CELL_W, CELL_H,
    NEST_RADIUS, FOOD_RADIUS,
    COL_BG, COL_NEST, COL_FOOD, COL_ANT, COL_ANT_FOOD,
    COL_PHEROMONE, COL_HUD, COL_QUEEN,
    GENE_MIN, GENE_MAX,
)

# Pre-allocate the pheromone surface once
_phero_surface: pygame.Surface | None = None
_cell_w_px = int(CELL_W)
_cell_h_px = int(CELL_H)


def _gene_colour(value: float) -> tuple[int, int, int]:
    """
    Map a gene value in [GENE_MIN, GENE_MAX] to a colour.
    Low (0.5) → cool blue.  High (1.5) → warm red.  Mid (1.0) → grey.
    Used to tint ants by speed gene so genetic variation is visible.
    """
    t = (value - GENE_MIN) / (GENE_MAX - GENE_MIN)   # 0.0 – 1.0
    r = int(80  + t * 160)   # 80 → 240
    g = int(220 - t * 140)   # 220 → 80
    b = int(180 - t * 130)   # 180 → 50
    return (r, g, b)


def render(screen: pygame.Surface, sim, clock: pygame.time.Clock):
    """Draw one complete frame onto *screen* and flip the display."""
    global _phero_surface

    # ── Background ────────────────────────────────────────────────────────────
    screen.fill(COL_BG)

    # ── Pheromone heatmap ────────────────────────────────────────────────────
    if _phero_surface is None:
        _phero_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

    _phero_surface.fill((0, 0, 0, 0))

    pr, pg, pb = COL_PHEROMONE
    for gy in range(PHEROMONE_GRID_HEIGHT):
        for gx in range(PHEROMONE_GRID_WIDTH):
            strength = sim.pheromone_grid[gy][gx]
            if strength <= 0:
                continue
            alpha = int(strength / 255 * 180)
            px    = int(gx * CELL_W)
            py    = int(gy * CELL_H)
            _phero_surface.fill((pr, pg, pb, alpha),
                                rect=(px, py, _cell_w_px, _cell_h_px))

    screen.blit(_phero_surface, (0, 0))

    # ── Nest ──────────────────────────────────────────────────────────────────
    nx, ny = sim.nest_pos
    pygame.draw.circle(screen, COL_NEST, (nx, ny), NEST_RADIUS)
    pygame.draw.circle(screen, (255, 120, 100), (nx, ny), NEST_RADIUS, 3)

    # ── Food sources ──────────────────────────────────────────────────────────
    font_small = pygame.font.SysFont("consolas", 12)
    for node in sim.food_sources:
        # Color brightness indicates remaining supply
        brightness = int(255 * (node.amount / max(1, node.max_amount)))
        color = (0, brightness, 0)
        
        radius = FOOD_RADIUS
        pygame.draw.circle(screen, color, (int(node.x), int(node.y)), radius)
        pygame.draw.circle(screen, (150, 255, 160), (int(node.x), int(node.y)), radius, 2)
        
        # Draw amount text
        amount_text = font_small.render(str(node.amount), True, (255, 255, 255))
        screen.blit(amount_text, (int(node.x) - 5, int(node.y) - 5))

    # ── Workers ───────────────────────────────────────────────────────────────
    for ant in sim.ants:
        if ant.carrying_food:
            colour = COL_ANT_FOOD
        else:
            # Tint by speed gene so genetic variation is visible
            colour = _gene_colour(ant.genes.get('speed', 1.0))

        px, py = int(ant.x), int(ant.y)
        pygame.draw.circle(screen, colour, (px, py), 4)

        # Tiny energy bar above the dot
        bar_w  = 8
        bar_h  = 2
        filled = int(bar_w * max(0, ant.energy / 100))
        pygame.draw.rect(screen, (50, 50, 50),   (px - bar_w // 2, py - 8, bar_w, bar_h))
        pygame.draw.rect(screen, (100, 220, 80), (px - bar_w // 2, py - 8, filled, bar_h))

    # ── Queen ─────────────────────────────────────────────────────────────────
    if sim.queen.alive:
        qx, qy = int(sim.queen.x), int(sim.queen.y)
        # Pulsing glow ring (radius oscillates with frame)
        pulse = int(4 * abs(math.sin(sim.frame * 0.05)))
        pygame.draw.circle(screen, (*COL_QUEEN, 60),
                           (qx, qy), 16 + pulse, 3)
        # Queen body
        pygame.draw.circle(screen, COL_QUEEN, (qx, qy), 10)
        pygame.draw.circle(screen, (255, 200, 240), (qx, qy), 10, 2)  # highlight rim

    # ── HUD ───────────────────────────────────────────────────────────────────
    font     = pygame.font.SysFont("consolas", 18)
    hud_x    = 10
    hud_y    = 10
    hud_line = 22

    lines = [
        (f"FPS:      {clock.get_fps():.1f}",           COL_HUD),
        (f"Frame:    {sim.frame}",                      COL_HUD),
        (f"Workers:  {len(sim.ants)}",                  COL_HUD),
        (f"Food:     {sim.food_collected}",             COL_FOOD),
        (f"Storage:  {sim.food_storage}",               (200, 160, 80)),
        (f"Queen Gen:{sim.queen.generation}",           COL_QUEEN),
        (f"Born:     {sim.queen.workers_born}",         COL_QUEEN),
    ]
    for i, (text, col) in enumerate(lines):
        surf = font.render(text, True, col)
        screen.blit(surf, (hud_x, hud_y + i * hud_line))

    # ── Queen gene readout (bottom-right) ─────────────────────────────────────
    gfont = pygame.font.SysFont("consolas", 14)
    gene_lines = [
        f"sensitivity: {sim.queen.genes['sensitivity']:.3f}",
        f"speed:       {sim.queen.genes['speed']:.3f}",
        f"boldness:    {sim.queen.genes['boldness']:.3f}",
        f"lifespan:    {sim.queen.genes['lifespan']:.3f}",
        f"efficiency:  {sim.queen.genes['energy_efficiency']:.3f}",
    ]
    for i, text in enumerate(reversed(gene_lines)):
        s = gfont.render(text, True, COL_QUEEN)
        screen.blit(s, (WINDOW_WIDTH - s.get_width() - 10,
                        WINDOW_HEIGHT - 14 - i * 18))

    # ── State legend (bottom-left) ────────────────────────────────────────────
    lfont = pygame.font.SysFont("consolas", 14)
    legend = [
        ("wander",           (180, 180, 180)),
        ("follow pheromone", COL_PHEROMONE),
        ("seek food",        COL_FOOD),
        ("return nest",      COL_ANT_FOOD),
    ]
    for i, (label, col) in enumerate(legend):
        s = lfont.render(f"\u25a0 {label}", True, col)
        screen.blit(s, (10, WINDOW_HEIGHT - 20 - i * 18))

    pygame.display.flip()


# math needed for Queen pulse — import at module level
import math
