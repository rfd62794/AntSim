# main.py — Entry point for AntSim (Phase 2A: Queen + Genes)
import sys
import pygame
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from sim import Simulation
from render import render


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("AntSim — Phase 2A: Queen Colony")
    clock  = pygame.time.Clock()

    sim     = Simulation()
    running = True

    header = (f"{'Frame':>7}  {'FPS':>6}  {'Ants':>5}  "
              f"{'Food':>5}  {'Stor':>5}  {'QGen':>5}")
    print("AntSim Phase 2A — Queen Colony")
    print("Close the window or press Q to quit.\n")
    print(header)
    print("-" * len(header))

    report_interval = FPS * 5   # every 5 seconds

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

        if sim.frame % report_interval == 0 and sim.frame > 0:
            print(f"{sim.frame:>7}  {clock.get_fps():>6.1f}  "
                  f"{len(sim.ants):>5}  {sim.food_collected:>5}  "
                  f"{sim.food_storage:>5}  {sim.queen.generation:>5}")

    pygame.quit()
    print(f"\nSimulation ended at frame {sim.frame}.")
    print(f"Total food collected : {sim.food_collected}")
    print(f"Queen generation     : {sim.queen.generation}")
    print(f"Total workers born   : {sim.queen.workers_born}")
    print(f"Workers alive at exit: {len(sim.ants)}")
    sys.exit(0)


if __name__ == "__main__":
    main()
