# main.py — Entry point for AntSim (Phase 2A: Queen + Genes)
import sys
import os
import json
import pygame
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
import constants
from sim import Simulation
from render import render_overworld

def load_tuning_config(config_file):
    """Load tuning configuration if provided"""
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return None


def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else None
    tuning_config = load_tuning_config(config_file) if config_file else None

    if tuning_config:
        # Override constants with config values
        constants.QUEEN_DEATH_CHANCE_PER_GEN = tuning_config.get('QUEEN_DEATH_CHANCE_PER_GEN', constants.QUEEN_DEATH_CHANCE_PER_GEN)
        SIMULATION_FRAMES = tuning_config.get('SIMULATION_FRAMES', 3600)
        HEADLESS_MODE = tuning_config.get('HEADLESS_MODE', False)
        OUTPUT_FILE = tuning_config.get('OUTPUT_FILE', None)
    else:
        HEADLESS_MODE = False
        OUTPUT_FILE = None
        SIMULATION_FRAMES = 3600

    if HEADLESS_MODE:
        import sim
        sim.QUEEN_DEATH_CHANCE_PER_GEN = constants.QUEEN_DEATH_CHANCE_PER_GEN
        # Ensure it affects Queen instances
        from queen import Queen
        simulation = Simulation()
        simulation.queen.death_chance_per_gen = constants.QUEEN_DEATH_CHANCE_PER_GEN
        
        for frame in range(SIMULATION_FRAMES):
            simulation.update()
            
            if frame > 0 and frame % 600 == 0:
                print(f"Frame {frame} | Ants: {len(simulation.ants)} | Food: {simulation.food_collected}")
                
        final_metrics = {
            'run_number': 0,
            'final_ants': len(simulation.ants),
            'final_food': simulation.food_collected,
            'final_generations': simulation.queen.generation,
            'final_queen_alive': simulation.queen.alive
        }
        
        if OUTPUT_FILE:
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(final_metrics, f)
        
        print(f"\nFinal: Ants={len(simulation.ants)} Food={simulation.food_collected} Gen={simulation.queen.generation} Alive={simulation.queen.alive}")
        sys.exit(0)

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("AntSim — Phase 2A: Queen Colony")
    clock  = pygame.time.Clock()

    simulation = Simulation()
    running = True

    print("AntSim Phase 3 — Hybrid View")
    print("Close the window or press Q to quit.\n")

    report_interval = FPS * 5   # every 5 seconds

    # Create surfaces for split-view
    overworld_surface = pygame.Surface((800, 400))
    nest_surface = pygame.Surface((800, 200))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False

        simulation.update()
        
        # Render Overworld (Top 2/3)
        render_overworld(overworld_surface, simulation, clock)
        
        # Render Nest (Bottom 1/3)
        simulation.nest_renderer.render_nest(
            nest_surface, 
            simulation.nest, 
            simulation.queen, 
            simulation.ants_in_nest, 
            simulation.food_storage
        )

        # Blit to screen
        screen.blit(overworld_surface, (0, 0))
        screen.blit(nest_surface, (0, 400))
        
        # Border between views
        pygame.draw.line(screen, (100, 100, 100), (0, 400), (800, 400), 2)
        
        pygame.display.flip()
        clock.tick(FPS)

        if simulation.frame % report_interval == 0 and simulation.frame > 0:
            alive_str = "Yes" if simulation.queen.alive else ("No (EMERGENCY)" if simulation.emergency_queen_mode else "Yes (NEW)")
            print(f"Frame {simulation.frame:>3}  | FPS: {clock.get_fps():>4.1f} | Ants: {len(simulation.ants) + len(simulation.ants_in_nest):>2} ({len(simulation.ants_in_nest)} in nest) | Food: {simulation.food_collected:>3} | Storage: {simulation.food_storage:>2} | RJ: {simulation.royal_jelly} | QGen: {simulation.queen.generation:>2} | Alive: {alive_str}")
            print(f"           | Life: {simulation.queen.genes['lifespan']:.2f} | Eff: {simulation.queen.genes['energy_efficiency']:.2f}")

        if simulation.frame == SIMULATION_FRAMES:
            pygame.image.save(screen, "screenshot_phase3.png")
            
        if simulation.frame > SIMULATION_FRAMES + 5:
             running = False

    pygame.quit()
    print(f"\nSimulation ended at frame {simulation.frame}.")
    print(f"Total food collected : {simulation.food_collected}")
    print(f"Queen generation     : {simulation.queen.generation}")
    print(f"Total workers born   : {simulation.queen.workers_born}")
    print(f"Workers alive at exit: {len(simulation.ants)}")
    sys.exit(0)


if __name__ == "__main__":
    main()
