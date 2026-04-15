# AntSim Phase 2A — Queen + Colony Structure Directive
**For:** IDE Pair Programming Agent  
**Status:** Ready to execute  
**Timeline:** 4-6 hours  
**Language:** Python 3.10+  
**Framework:** Pygame 2.x (extending Phase 1 codebase)  

---

## Objective

Replace individual ant autonomy with **Queen-driven colony structure**. Queen has 3 genes (sensitivity, speed, boldness). All workers born from Queen inherit her genes + mutation. Watch colony emerge from Queen's genetics.

---

## Core Changes

### **A. Queen Class**

```python
class Queen:
    def __init__(self, x, y, genes=None):
        self.x = x
        self.y = y
        self.energy = 200  # Queens need more energy
        self.alive = True
        
        # Queen's genes (inherited by all workers)
        if genes is None:
            self.genes = {
                'sensitivity': 1.0,
                'speed': 1.0,
                'boldness': 0.5
            }
        else:
            self.genes = genes
        
        self.generation = 0
        self.workers_born = 0
```

### **B. Worker Birth Mechanic**

**Queen produces workers based on food available:**

```python
def queen_reproduce(queen, food_available):
    """Queen produces 1 worker when conditions are met"""
    
    # Reproduction threshold: 20 food units in storage
    if food_available >= 20:
        # Create worker with Queen's genes + mutation
        worker_genes = {}
        for gene in ['sensitivity', 'speed', 'boldness']:
            base = queen.genes[gene]
            
            # Small mutation: ±5% chance to shift by ±5%
            if random.random() < 0.05:
                base *= random.uniform(0.95, 1.05)
            
            # Clamp to 0.5-1.5
            worker_genes[gene] = max(0.5, min(1.5, base))
        
        worker = Ant(queen.x, queen.y, genes=worker_genes)
        queen.workers_born += 1
        
        return worker  # Return to add to sim.ants
    
    return None
```

### **C. Ant Class Modifications**

**Ants now store which Queen they came from (optional, for tracking):**

```python
class Ant:
    def __init__(self, x, y, genes=None, queen_id=None):
        self.x = x
        self.y = y
        self.energy = 100
        self.carrying_food = False
        self.state = "wander"
        self.queen_id = queen_id  # Track lineage
        
        # Genes (inherited from Queen)
        if genes is None:
            self.genes = {
                'sensitivity': 1.0,
                'speed': 1.0,
                'boldness': 0.5
            }
        else:
            self.genes = genes
        
        self.actual_speed = ANT_SPEED * self.genes['speed']
        self.pheromone_range = PHEROMONE_DETECT_RANGE * self.genes['sensitivity']
```

### **D. Simulation Class Changes**

**Add Queen to Simulation:**

```python
class Simulation:
    def __init__(self):
        self.ants = []
        self.queen = Queen(400, 300)  # Spawn Queen at nest center
        self.food_sources = []
        self.nest_pos = NEST_POS
        self.pheromone_grid = [[0 for _ in range(PHEROMONE_GRID_WIDTH)] 
                               for _ in range(PHEROMONE_GRID_HEIGHT)]
        self.food_collected = 0
        self.food_storage = 0  # Food in nest (available for reproduction)
        self.frame = 0
        
        # Spawn initial worker cohort (10 ants from Queen)
        for _ in range(10):
            worker = Ant(400, 300, genes=self.queen.genes.copy())
            self.ants.append(worker)
```

**In update() method, add Queen reproduction:**

```python
def update(self):
    # ... existing ant update code ...
    
    # Queen reproduction
    if self.queen.alive and self.frame % 60 == 0:  # Check every 1 second
        new_worker = queen_reproduce(self.queen, self.food_storage)
        if new_worker:
            self.ants.append(new_worker)
            self.food_storage -= 20  # Cost of reproduction
            self.queen.generation += 1
    
    # ... rest of update ...
```

**When food reaches nest:**

```python
# When ant returns food to nest (existing logic)
if ant_touching_nest and ant.carrying_food:
    self.food_collected += 1
    self.food_storage += 1  # Add to Queen's food reserves
    ant.carrying_food = False
    ant.energy = 100
```

---

## Behavior Integration (Genes Affect Worker Behavior)

### **Pheromone Sensitivity**

Worker with high sensitivity detects pheromone from farther away:

```python
# In ant.update()
detected = sim.get_pheromone_strength(self.x, self.y)

# High sensitivity = more likely to detect and follow
if detected > 5 and random.random() < self.genes['sensitivity']:
    self.state = "follow_pheromone"
```

### **Speed**

Worker speed is multiplied by gene:

```python
# In ant.update()
self.actual_speed = ANT_SPEED * self.genes['speed']

# Movement uses actual_speed instead of ANT_SPEED
if self.state == "wander":
    # Move by actual_speed pixels instead of fixed ANT_SPEED
    self.x += direction_x * self.actual_speed
    self.y += direction_y * self.actual_speed
```

### **Boldness**

Worker with high boldness explores more, low boldness follows trails:

```python
# In ant.update()
if self.state == "wander":
    # High boldness = keep wandering
    # Low boldness = switch to follow pheromone if available
    if self.genes['boldness'] < 0.5 and detected_pheromone > 10:
        self.state = "follow_pheromone"
```

---

## Render Changes

### **Draw Queen**

```python
# In render.py, in render() function
# Draw Queen as larger circle at nest
pygame.draw.circle(screen, (255, 100, 100), (int(queen.x), int(queen.y)), 8)
```

### **Stats Display**

```python
# Add to stats display
queen_stats = f"Queen Gen: {sim.queen.generation} | Food Storage: {sim.food_storage} | Workers: {len(sim.ants)}"
screen.blit(font.render(queen_stats, True, (255, 255, 255)), (10, 40))
```

---

## Acceptance Criteria

✅ Queen spawns at nest center  
✅ Queen is visually distinct (larger, different color)  
✅ Initial worker cohort (10 ants) inherit Queen's genes  
✅ Ants with different genes behave differently (visibly)  
✅ Food collection increments food_storage  
✅ Every 20 food collected, Queen produces 1 new worker  
✅ New workers inherit Queen's genes + small mutation  
✅ Colony grows as food accumulates  
✅ Stats show Queen generation, food storage, worker count  
✅ Runs 60 FPS for 5+ minutes without crash  

---

## Success Checkpoint

**You run it and observe:**
- Queen at center (larger, red)
- 10 initial workers forage
- Ants with different genes move/behave differently (fast vs slow, bold explorers vs careful followers)
- Food counter goes up
- Every ~20 food, new worker spawns (generation counter increments)
- Colony grows smoothly
- Stats update in real-time

**Terminal output shows:**
```
Frame 300 | FPS: 60.2 | Ants: 12 | Food: 15 | Storage: 8 | Queen Gen: 1
Frame 600 | FPS: 59.8 | Ants: 14 | Food: 35 | Storage: 5 | Queen Gen: 2
Frame 900 | FPS: 60.1 | Ants: 16 | Food: 57 | Storage: 0 | Queen Gen: 3
```

**If successful:** Queen-driven colony is alive. You can now add pressures (food scarcity, predators) and watch colony adapt through Queen's genetics.

---

## What NOT to Do

- ❌ Don't add multiple Queens yet
- ❌ Don't add Queen death/replacement
- ❌ Don't add male ants or mating
- ❌ Don't add specialized roles (soldiers, nurses)
- ❌ Don't add breeding UI or player control

---

## Hand-off

**When done:**
1. Commit code to `/home/claude/AntSim/`
2. Run `python main.py`, let it run for 60 seconds
3. Show **screenshot** of colony at 60 seconds (Queen visible, workers around nest, pheromone trails visible)
4. Show **terminal output** proving:
   - 60 FPS stable
   - Ant count growing (via reproduction)
   - Food storage management working
5. Show **observation**: "Queen spawned X generations, colony is Y ants large, stable growth"

**Critical:** Show the actual working simulation, not summaries. Robert requires proof.

---

**Directive Created:** April 14, 2026  
**Target Completion:** Today EOD  
**Owner:** Robert (rfd62794)
