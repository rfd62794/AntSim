import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from sim import Simulation
from constants import EMERGENCY_QUEEN_DEV_TIME

# Force init surface but headlessly
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

chances = [0.02, 0.05, 0.10, 0.15, 0.20]

print("--- Phase 2C Tuning Experiments ---")
for chance in chances:
    print(f"\nRunning sim with QUEEN_DEATH_CHANCE_PER_GEN = {chance}")
    
    # Override chance in sim:
    from constants import QUEEN_DEATH_CHANCE_PER_GEN
    sim = Simulation()
    sim.queen.death_chance_per_gen = chance
    
    queen_died = False
    colony_recovered = False
    
    for frame in range(3600):
        if not sim.queen.alive and not queen_died:
            queen_died = True
        
        sim.update()
        
        # Checking if she died then a new one came
        if queen_died and sim.queen.alive:
            colony_recovered = True
            
        if len(sim.ants) == 0:
            break
            
    print(f"Queen died? {'Yes' if queen_died else 'No'}")
    print(f"Colony recovered? {'Yes' if colony_recovered else 'No'}")
    print(f"Final Ant Count:   {len(sim.ants)}")
    print(f"Final Food:        {sim.food_collected}")
    print(f"Final Generation:  {sim.queen.generation}")
    print(f"Final RJ:          {sim.royal_jelly}")
    print(f"Final Q.Lifespan:  {sim.queen.genes['lifespan']:.3f} | Q.Efficiency: {sim.queen.genes['energy_efficiency']:.3f}")
