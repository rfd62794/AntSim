# main.py — Entry point for AntSim MVP
import sys
import pygame
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from sim import Simulation
from render import render


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("AntSim MVP — Phase 1")
    clock  = pygame.time.Clock()

    sim     = Simulation()
    running = True

    print("AntSim started. Close the window or press Q to quit.")
    print(f"{'Frame':>7}  {'FPS':>6}  {'Ants':>5}  {'Food':>6}")

    report_interval = FPS * 5  # print status every 5 seconds

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False

        sim.update()
        render(screen, sim, clock)
        clock.tick(FPS)

        # Periodic terminal report
        if sim.frame % report_interval == 0 and sim.frame > 0:
            print(f"{sim.frame:>7}  {clock.get_fps():>6.1f}  "
                  f"{len(sim.ants):>5}  {sim.food_collected:>6}")

    pygame.quit()
    print(f"\nSimulation ended at frame {sim.frame}.")
    print(f"Total food collected: {sim.food_collected}")
    sys.exit(0)


if __name__ == "__main__":
    main()
