import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
pygame.init()

from constants import WINDOW_WIDTH, WINDOW_HEIGHT
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

from sim import Simulation
from render import render_overworld

sim = Simulation()
# Run for a while to get some activity
for i in range(1200):
    sim.update()

# Create surfaces for split-view
overworld_surface = pygame.Surface((800, 400))
nest_surface = pygame.Surface((800, 200))

# Render both
render_overworld(overworld_surface, sim, clock)
sim.nest_renderer.render_nest(nest_surface, sim.nest, sim.queen, sim.ants_in_nest, sim.food_storage)

# Blit to screen
screen.blit(overworld_surface, (0, 0))
screen.blit(nest_surface, (0, 400))
pygame.draw.line(screen, (100, 100, 100), (0, 400), (800, 400), 2)

pygame.image.save(screen, "screenshots/screenshot_phase3.png")
print("Saved screenshot_phase3.png")
