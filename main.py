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

    print("AntSim Phase 2B — Evolution Scarcity")
    print("Close the window or press Q to quit.\n")

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
            print(f"Frame {sim.frame:>3}  | FPS: {clock.get_fps():>4.1f} | Ants: {len(sim.ants):>2} | Food: {sim.food_collected:>3} | Storage: {sim.food_storage:>2} | QGen: {sim.queen.generation:>2}")
            print(f"           | Life: {sim.queen.genes['lifespan']:.2f} | Eff: {sim.queen.genes['energy_efficiency']:.2f}")

        if sim.frame == 3600:
            pygame.image.save(screen, "screenshot_phase2b.png")
            
        if sim.frame > 3605:
            running = False

    pygame.quit()
    print(f"\nSimulation ended at frame {sim.frame}.")
    print(f"Total food collected : {sim.food_collected}")
    print(f"Queen generation     : {sim.queen.generation}")
    print(f"Total workers born   : {sim.queen.workers_born}")
    print(f"Workers alive at exit: {len(sim.ants)}")
    sys.exit(0)


if __name__ == "__main__":
    main()
