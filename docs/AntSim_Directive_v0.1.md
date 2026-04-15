# AntSim MVP — Implementation Directive
**For:** IDE Pair Programming Agent (Antigravity/VS Code)  
**Status:** Ready to execute  
**Timeline:** 2-4 hours (including testing + debug)  
**Language:** Python 3.10+  
**Framework:** Pygame 2.x  

---

## Execution Plan

### Phase A: Project Setup (15 min)
1. Create `/home/claude/AntSim/` directory
2. Create `venv`, activate, `pip install pygame`
3. Create `main.py` (entry point)
4. Create `constants.py` (all magic numbers)
5. Create `ant.py` (Ant class)
6. Create `sim.py` (Simulation class)
7. Create `render.py` (Pygame rendering)

### Phase B: Core Data Structures (30 min)
**In `constants.py`:**
```python
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
NEST_POS = (400, 300)
NEST_RADIUS = 50
ANT_COUNT = 10
FOOD_COUNT = 5
FOOD_RADIUS = 20

# Ant constants
ANT_SPEED = 2
ANT_ENERGY_MAX = 100
ANT_ENERGY_DRAIN = 0.5
ANT_VISION_RANGE = 100
PHEROMONE_DETECT_RANGE = 40
PHEROMONE_EMIT = 50

# Pheromone grid
PHEROMONE_GRID_WIDTH = 80
PHEROMONE_GRID_HEIGHT = 60
PHEROMONE_DECAY = 0.95
PHEROMONE_THRESHOLD = 5
```

**In `ant.py`:**
```python
class Ant:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0  # velocity x
        self.vy = 0  # velocity y
        self.energy = 100
        self.carrying_food = False
        self.state = "wander"  # ["wander", "follow_pheromone", "seek_food", "return_nest"]
    
    def update(self, food_sources, nest_pos, pheromone_grid):
        # Stub: update position, state, energy
        pass
    
    def is_alive(self):
        return self.energy > 0
```

**In `sim.py`:**
```python
class Simulation:
    def __init__(self):
        self.ants = [Ant(400, 300) for _ in range(ANT_COUNT)]
        self.food_sources = []  # List of (x, y, amount)
        self.nest_pos = NEST_POS
        self.pheromone_grid = [[0 for _ in range(PHEROMONE_GRID_WIDTH)] 
                               for _ in range(PHEROMONE_GRID_HEIGHT)]
        self.food_collected = 0
        self.frame = 0
    
    def update(self):
        # For each ant: update, check collisions, emit pheromone
        # Decay pheromone
        # Remove dead ants
        # Respawn food if depleted
        pass
    
    def get_pheromone_strength(self, x, y):
        # Convert pixel coords to grid, return strength
        pass
```

### Phase C: Ant Behavior (1 hour)
**Implement in `ant.py`:**

1. **Random walk (wander state):**
   - Change direction every 20-40 frames (random)
   - Emit pheromone at current position
   - Energy -= drain

2. **Pheromone following:**
   - Check pheromone in 40px radius
   - If found, move toward strongest cell
   - Emit pheromone
   - Energy -= drain

3. **Food seeking:**
   - If no pheromone visible, check vision range (100px)
   - If food found, move toward it
   - Emit pheromone
   - Energy -= drain

4. **Nest return:**
   - When touching food, set `carrying_food = True`
   - Navigate back to nest using pheromone + direct path
   - When touching nest, drop food, reset energy

5. **Death:**
   - When energy <= 0, mark as dead

### Phase D: Pheromone System (45 min)
**Implement in `sim.py`:**

1. **Per-frame pheromone emission:**
   - When ant moves, find grid cell at (ant.x, ant.y)
   - `pheromone_grid[grid_y][grid_x] = min(255, strength + PHEROMONE_EMIT)`

2. **Decay:**
   - Every frame: `pheromone_grid[y][x] *= PHEROMONE_DECAY`
   - If < 5, set to 0

3. **Query:**
   - `get_pheromone_strength(x, y)` returns grid value at that position

### Phase E: Collision & State (30 min)
**Implement in `sim.py`:**

1. **Food pickup:**
   - Check if ant position within `food_radius` of food source
   - If yes: `ant.carrying_food = True`, remove food from source

2. **Nest return:**
   - Check if ant within `nest_radius` of nest
   - If carrying food: increment `food_collected`, reset energy, set `carrying_food = False`

3. **Dead ant cleanup:**
   - Remove ants where `is_alive() == False`

4. **Food respawn:**
   - If all food gone, respawn 5 random sources

### Phase F: Rendering (45 min)
**Implement in `render.py`:**

```python
def render(screen, sim):
    screen.fill((0, 0, 0))  # Black background
    
    # Draw pheromone heatmap
    for y in range(PHEROMONE_GRID_HEIGHT):
        for x in range(PHEROMONE_GRID_WIDTH):
            strength = sim.pheromone_grid[y][x]
            if strength > 0:
                # Draw semi-transparent blue rect
                pixel_x = x * (WINDOW_WIDTH / PHEROMONE_GRID_WIDTH)
                pixel_y = y * (WINDOW_HEIGHT / PHEROMONE_GRID_HEIGHT)
                alpha = int(strength / 255 * 100)
                # pygame.draw.rect with alpha
    
    # Draw food sources
    for fx, fy, amount in sim.food_sources:
        pygame.draw.circle(screen, (0, 255, 0), (int(fx), int(fy)), FOOD_RADIUS)
    
    # Draw nest
    pygame.draw.circle(screen, (255, 0, 0), sim.nest_pos, NEST_RADIUS)
    
    # Draw ants
    for ant in sim.ants:
        pygame.draw.circle(screen, (255, 255, 255), (int(ant.x), int(ant.y)), 3)
    
    # Draw stats
    font = pygame.font.Font(None, 24)
    stats = f"FPS: {clock.get_fps():.1f} | Ants: {len(sim.ants)} | Food: {sim.food_collected}"
    screen.blit(font.render(stats, True, (255, 255, 255)), (10, 10))
    
    pygame.display.flip()
```

### Phase G: Main Loop (15 min)
**Implement in `main.py`:**

```python
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("AntSim MVP")
    clock = pygame.time.Clock()
    
    sim = Simulation()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        sim.update()
        render(screen, sim)
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()
```

### Phase H: Testing & Debug (30 min)
**Manual tests:**
1. Launch sim, watch for 30 seconds
2. Verify ants move
3. Verify pheromone trails appear (blue overlay)
4. Verify ants pick up food (visual disappearance)
5. Verify food counter increments
6. Verify ants die when out of energy
7. Verify food respawns

**If crash:** Print stack trace, identify issue, patch

---

## Acceptance Criteria

✅ Sim launches without error  
✅ Ants spawn in nest  
✅ Ants move (wandering)  
✅ Pheromone grid updates (visible as blue heatmap)  
✅ Ants follow pheromone toward food  
✅ Ants pick up food and return to nest  
✅ Food counter increments when food reaches nest  
✅ Ants die when energy depletes  
✅ Food respawns when all sources empty  
✅ Runs 60 FPS for 5+ minutes without crash  

---

## Success Checkpoint

**You run it, watch for 2 minutes, and think:**
*"Huh, the ants actually cooperate without being told to. That's neat."*

If yes: Commit to repo, create README, mark Phase 1 done.  
If no: Debug the specific failure, retry.

---

## What Agent Should NOT Do

- ❌ Add UI sliders/parameters yet
- ❌ Optimize rendering (keep it simple)
- ❌ Add multiple colonies
- ❌ Add genetics
- ❌ Polish graphics
- ❌ Over-engineer class hierarchy

---

## Hand-off

**When done:**
1. Commit all code to `/home/claude/AntSim/` (or push to GitHub)
2. Create `README.md` with:
   - How to run (`python main.py`)
   - What you're watching
   - Next phases (genetics, breeding)
3. Show Robert a screenshot or 30-second video of it running
4. **Critical:** Show raw terminal output confirming FPS, ant count, food collected

**Do NOT hand off** with just "I think it works." Show the actual output.

---

**Directive Created:** April 14, 2026  
**Target Completion:** April 14, 2026 EOD  
**Owner:** Robert (rfd62794)
