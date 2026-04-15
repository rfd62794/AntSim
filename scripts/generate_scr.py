import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
pygame.init()

from constants import WINDOW_WIDTH, WINDOW_HEIGHT
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

from sim import Simulation
from render import render

sim = Simulation()
for i in range(3600):
    sim.update()

# Force a render
render(screen, sim, clock)
pygame.image.save(screen, "screenshots\screenshot_phase2c.png")
print("Saved screenshot_phase2c.png")
