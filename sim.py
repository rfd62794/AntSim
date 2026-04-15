# sim.py — Simulation state and update logic
import math
import random
from ant import Ant
from queen import Queen
from constants import (
    ANT_COUNT, ANT_COUNT_MAX,
    FOOD_COUNT, FOOD_RADIUS, NEST_POS, NEST_RADIUS, FOOD_START_AMOUNT,
    ANT_ENERGY_MAX,
    QUEEN_REPRO_COST, QUEEN_REPRO_INTERVAL,
    FOOD_TO_ROYAL_JELLY_RATIO, EMERGENCY_QUEEN_DEV_TIME,
    PHEROMONE_GRID_WIDTH, PHEROMONE_GRID_HEIGHT,
    PHEROMONE_DECAY, PHEROMONE_THRESHOLD,
    WINDOW_WIDTH, WINDOW_HEIGHT,
    CELL_W, CELL_H,
)
from nest import NestStructure
from render_nest import NestRenderer

# Minimum distance a food source must be from the nest
_FOOD_SPAWN_MIN_DIST = 100

class FoodNode:
    def __init__(self, x: float, y: float, amount: int = FOOD_START_AMOUNT):
        self.x = x
        self.y = y
        self.amount = amount
        self.max_amount = amount
        self.active = True
    
    def take_food(self, quantity: int = 1) -> int:
        """Remove food from this node"""
        if self.amount > 0:
            self.amount -= quantity
            if self.amount <= 0:
                self.active = False
            return quantity
        return 0
    
    def is_depleted(self) -> bool:
        return self.amount <= 0


def _spawn_food_sources(n: int) -> list:
    """Generate n food sources at random positions, away from the nest."""
    sources = []
    nx, ny  = NEST_POS
    while len(sources) < n:
        x = random.randint(FOOD_RADIUS + 5, WINDOW_WIDTH  - FOOD_RADIUS - 5)
        y = random.randint(FOOD_RADIUS + 5, WINDOW_HEIGHT - FOOD_RADIUS - 5)
        if math.hypot(x - nx, y - ny) >= _FOOD_SPAWN_MIN_DIST:
            sources.append(FoodNode(x, y, amount=FOOD_START_AMOUNT))
    return sources


class Simulation:
    """Owns all simulation state.  Call update() once per frame."""

    def __init__(self):
        self.nest_pos    = NEST_POS
        self.queen       = Queen(*NEST_POS)
        self.food_sources = _spawn_food_sources(FOOD_COUNT)

        # 2-D list [row][col] of pheromone strengths (0-255)
        self.pheromone_grid = [[0.0] * PHEROMONE_GRID_WIDTH
                               for _ in range(PHEROMONE_GRID_HEIGHT)]

        self.food_collected = 0
        self.food_storage   = 0   # food units banked in the nest (fuels reproduction)
        self.frame          = 0

        self.ants = [
            Ant(*NEST_POS, genes=dict(self.queen.genes), queen_id=id(self.queen))
            for _ in range(ANT_COUNT)
        ]

        # ── State / Meta ──────────────────────────────────────────────────────
        self.royal_jelly = 0
        self.emergency_queen_mode = False
        self.emergency_queen_candidate = None

    # ──────────────────────────────────────────────────────────────────────────
    # Public
    # ──────────────────────────────────────────────────────────────────────────

    def update(self):
        self.frame += 1

        # 1. Update ants (movement + state)
        for ant in self.ants:
            if ant.is_alive():
                ant.update(self.food_sources, self.nest_pos, self.pheromone_grid)

        # 2. Collisions: food pickup
        self._check_food_pickup()

        # 3. Collisions: nest drop-off (also increments food_storage)
        self._check_nest_dropoff()

        # 4. Emit pheromone
        for ant in self.ants:
            if ant.is_alive():
                ant.emit_pheromone(self.pheromone_grid)

        # 5. Decay pheromone grid
        self._decay_pheromone()

        # 6. Remove dead ants
        self.ants = [a for a in self.ants if a.is_alive()]

        # 7. Queen Reproduction / Mortality
        if self.queen.alive:
            if self.frame > 0 and self.frame % 60 == 0:
                if self.queen.check_mortality():
                    # Queen just died
                    self.trigger_emergency_queen_rearing()

            if self.queen.alive and self.frame % QUEEN_REPRO_INTERVAL == 0:
                if len(self.ants) < ANT_COUNT_MAX:
                    new_worker = self.queen.try_reproduce(self.food_storage)
                    if new_worker is not None:
                        self.ants.append(new_worker)
                        self.food_storage -= QUEEN_REPRO_COST
        else:
            self.update_emergency_queen()

        # 8. Respawn food
        self.check_food_respawn()

        # 9. Verify antrance to nest / update nest occupants
        for ant in self.ants[:]:
            if self.check_ant_at_nest_entrance(ant):
                self.process_ant_nest_entry(ant)
        
        self.update_ants_in_nest()

    def check_food_respawn(self):
        """Remove depleted nodes, respawn new ones to maintain FOOD_COUNT"""
        self.food_sources = [fn for fn in self.food_sources if not fn.is_depleted()]
        
        while len(self.food_sources) < FOOD_COUNT:
            nx, ny = self.nest_pos
            x = random.randint(FOOD_RADIUS + 5, WINDOW_WIDTH  - FOOD_RADIUS - 5)
            y = random.randint(FOOD_RADIUS + 5, WINDOW_HEIGHT - FOOD_RADIUS - 5)
            if math.hypot(x - nx, y - ny) >= _FOOD_SPAWN_MIN_DIST:
                self.food_sources.append(FoodNode(x, y, amount=FOOD_START_AMOUNT))

    def get_pheromone_strength(self, x: float, y: float) -> float:
        """Return pheromone strength at pixel coordinate (x, y)."""
        gx = max(0, min(PHEROMONE_GRID_WIDTH  - 1, int(x / CELL_W)))
        gy = max(0, min(PHEROMONE_GRID_HEIGHT - 1, int(y / CELL_H)))
        return self.pheromone_grid[gy][gx]

    # ──────────────────────────────────────────────────────────────────────────
    # Internal
    # ──────────────────────────────────────────────────────────────────────────

    def _check_food_pickup(self):
        """Ants not carrying food that touch a food source pick it up."""
        for ant in self.ants:
            if ant.carrying_food or not ant.is_alive():
                continue
            for node in self.food_sources:
                if node.is_depleted():
                    continue
                if math.hypot(ant.x - node.x, ant.y - node.y) <= FOOD_RADIUS:
                    if node.take_food(1):
                        ant.carrying_food = True
                        ant.state = "return_nest"
                        break

    def _check_nest_dropoff(self):
        """Ants carrying food that touch the nest deposit to food_storage."""
        nx, ny = self.nest_pos
        for ant in self.ants:
            if not ant.carrying_food or not ant.is_alive():
                continue
            if math.hypot(ant.x - nx, ant.y - ny) <= NEST_RADIUS:
                ant.carrying_food = False
                # energy reset is no longer an instant full heal—it regens via update when holding food
                self.food_collected += 1
                self.food_storage   += 1             # bank food for Queen

                # If we are in emergency, converting food to jelly automatically
                if self.emergency_queen_mode and self.food_storage >= FOOD_TO_ROYAL_JELLY_RATIO:
                    self.food_storage -= FOOD_TO_ROYAL_JELLY_RATIO
                    self.royal_jelly += 1

    def trigger_emergency_queen_rearing(self):
        """Queen died, convert food to royal jelly to raise emergency candidate."""
        self.emergency_queen_mode = True
        
        while self.food_storage >= FOOD_TO_ROYAL_JELLY_RATIO:
            self.food_storage -= FOOD_TO_ROYAL_JELLY_RATIO
            self.royal_jelly += 1

    def update_emergency_queen(self):
        """Develop the emergency queen over time, consuming jelly."""
        if not self.emergency_queen_mode:
            return
            
        if self.emergency_queen_candidate is None:
            self.emergency_queen_candidate = {
                'start_frame': self.frame,
                'fed': False
            }
            
        if self.royal_jelly > 0:
            self.emergency_queen_candidate['fed'] = True
            self.royal_jelly -= 1
            
        elapsed = self.frame - self.emergency_queen_candidate['start_frame']
        if elapsed >= EMERGENCY_QUEEN_DEV_TIME:
            if self.emergency_queen_candidate['fed']:
                self.spawn_new_queen()
                self.emergency_queen_mode = False
                self.emergency_queen_candidate = None

    def spawn_new_queen(self):
        """Yield a new Queen built from average genetics of existing worker ants."""
        if len(self.ants) > 0:
            avg_genes = {
                'sensitivity': sum(ant.genes['sensitivity'] for ant in self.ants) / len(self.ants),
                'speed': sum(ant.genes['speed'] for ant in self.ants) / len(self.ants),
                'boldness': sum(ant.genes['boldness'] for ant in self.ants) / len(self.ants),
                'lifespan': sum(ant.genes['lifespan'] for ant in self.ants) / len(self.ants),
                'energy_efficiency': sum(ant.genes['energy_efficiency'] for ant in self.ants) / len(self.ants)
            }
            for gene in avg_genes:
                if random.random() < 0.1: # 10% mutation
                    avg_genes[gene] *= random.uniform(0.95, 1.05)
                # Keep within bounds from constants if we had access, but rough 0.5-1.5 clamp:
                avg_genes[gene] = max(0.5, min(1.5, avg_genes[gene]))
        else:
            avg_genes = self.queen.genes.copy()
            
        old_generation = self.queen.generation
        self.queen = Queen(self.nest_pos[0], self.nest_pos[1], genes=avg_genes)
        self.queen.generation = old_generation + 1

    def _decay_pheromone(self):
        """Multiply every cell by decay factor; zero out cells below threshold."""
        for row in self.pheromone_grid:
            for i in range(len(row)):
                v = row[i] * PHEROMONE_DECAY
                row[i] = v if v >= PHEROMONE_THRESHOLD else 0.0

    # ── Phase 3: Nest View Logic ────────────────────────────────────────────

    def check_ant_at_nest_entrance(self, ant) -> bool:
        """Check if ant reached nest entrance (center of map)"""
        nx, ny = self.nest_pos
        dist = math.hypot(ant.x - nx, ant.y - ny)
        # Entry threshold: must be near nest radius and either carrying food or low energy
        if dist < NEST_RADIUS + 5:
            if ant.carrying_food or ant.energy < ant.max_energy * 0.4:
                return True
        return False

    def process_ant_nest_entry(self, ant):
        """Move ant from overworld into the subterranean view"""
        if ant.in_nest: return

        # Determine destination chamber based on state
        if ant.carrying_food:
            chamber_id = 'storage'
            task = 'deposit_food'
        else:
            chamber_id = 'nursery' # Go rest/nursery if just low energy
            task = 'rest'

        ant.enter_nest(chamber_id)
        self.ants_in_nest.append(ant)
        if ant in self.ants:
            self.ants.remove(ant)
        
        ant.perform_task(task, duration=40)

    def process_ant_nest_exit(self, ant):
        """Move ant from nest back to overworld"""
        if not ant.in_nest: return

        # Finalize tasks before ejection
        if ant.task_complete_type == 'deposit_food':
            # Food collected / storage increments handled in _check_nest_dropoff?
            # Actually for Phase 3 we can move the math here or keep it in dropoff.
            # Directive says: self.food_storage += 1
            pass
        
        ant.exit_nest(self.nest_pos[0], self.nest_pos[1])
        self.ants_in_nest.remove(ant)
        self.ants.append(ant)

    def update_ants_in_nest(self):
        """Tick internal nest tasks"""
        to_exit = []
        for ant in self.ants_in_nest:
            # Queen energy also regens in nest? Simple for now:
            ant.energy = min(ant.max_energy, ant.energy + 2.0)
            
            completed = ant.update_task()
            if completed:
                # Capture result for exit processing
                ant.task_complete_type = completed
                to_exit.append(ant)
        
        for ant in to_exit:
            self.process_ant_nest_exit(ant)
