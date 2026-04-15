# AntSim Phase 2C — Queen Death + Royal Jelly + Emergency Queen Rearing
**For:** IDE Pair Programming Agent  
**Status:** Ready to execute  
**Timeline:** 6-8 hours  
**Language:** Python 3.10+  
**Framework:** Pygame 2.x (extending Phase 2B codebase)  

---

## Objective

Implement real queen mortality and colony recovery:
1. Queen can die (random chance per generation)
2. Workers detect queenlessness via pheromone absence
3. Workers feed best young larva with "royal jelly" (new resource)
4. After development time, new Queen emerges
5. New Queen immediately suppresses alternative reproduction

---

## Core Mechanics

### **A. Queen Mortality**

```python
class Queen:
    def __init__(self, x, y, genes=None):
        # ... existing code ...
        self.alive = True
        self.death_chance_per_gen = 0.05  # Tunable: 5% chance to die per generation
    
    def check_mortality(self):
        """Random queen death"""
        if random.random() < self.death_chance_per_gen:
            self.alive = False
            return True
        return False
```

**In Simulation.update():**
```python
def update(self):
    # ... existing code ...
    
    # Check queen mortality (once per generation, e.g., every 60 frames)
    if self.frame % 60 == 0:
        if self.queen.check_mortality():
            self.emergency_queen_mode = True
            self.emergency_queen_start_frame = self.frame
```

### **B. Royal Jelly Resource**

**New resource type in Simulation:**

```python
class Simulation:
    def __init__(self):
        # ... existing code ...
        self.royal_jelly = 0  # New resource
        self.emergency_queen_mode = False
        self.emergency_queen_start_frame = None
        self.emergency_queen_candidate = None  # The larva being fed
        self.emergency_queen_development_time = 240  # Frames (tunable, ~4 seconds at 60 FPS)
```

**Royal Jelly generation:**
- When Queen dies, workers generate royal jelly from food storage
- Cost: 30 food → 1 royal jelly (tunable)

```python
def trigger_emergency_queen_rearing(self):
    """When queen dies, convert food to royal jelly"""
    if self.food_storage >= 30:
        self.food_storage -= 30
        self.royal_jelly += 1
        
        # Find best young larva (simulated; pick youngest from any eggs laid in last N frames)
        # For MVP: just flag that we're looking for a queen candidate
        self.emergency_queen_mode = True
```

### **C. Emergency Queen Development**

**Track development progress:**

```python
def update_emergency_queen(self):
    """Develop emergency queen from larva"""
    
    if not self.emergency_queen_mode or self.royal_jelly == 0:
        return
    
    # Development is time-based
    if self.emergency_queen_candidate is None:
        # Select best young larva (youngest available)
        # For MVP: create a virtual "larva" that's developing
        self.emergency_queen_start_frame = self.frame
        self.emergency_queen_candidate = {
            'start_frame': self.frame,
            'fed': False
        }
    
    # Feed royal jelly to developing larva
    if self.royal_jelly > 0:
        self.emergency_queen_candidate['fed'] = True
        self.royal_jelly -= 1  # Consume 1 royal jelly
    
    # Check if development is complete
    development_elapsed = self.frame - self.emergency_queen_candidate['start_frame']
    if development_elapsed >= self.emergency_queen_development_time:
        # New queen emerges
        if self.emergency_queen_candidate['fed']:
            self.spawn_new_queen()
            self.emergency_queen_mode = False
            self.emergency_queen_candidate = None
```

### **D. New Queen Birth**

**Create new Queen from best genes of current workers:**

```python
def spawn_new_queen(self):
    """Emergency queen emerges from development"""
    
    # New queen inherits blend of best worker genes
    # (Simple: average of all current workers' genes)
    if len(self.ants) > 0:
        avg_genes = {
            'sensitivity': sum(ant.genes['sensitivity'] for ant in self.ants) / len(self.ants),
            'speed': sum(ant.genes['speed'] for ant in self.ants) / len(self.ants),
            'boldness': sum(ant.genes['boldness'] for ant in self.ants) / len(self.ants),
            'lifespan': sum(ant.genes['lifespan'] for ant in self.ants) / len(self.ants),
            'energy_efficiency': sum(ant.genes['energy_efficiency'] for ant in self.ants) / len(self.ants),
        }
        
        # Small mutations
        for gene in avg_genes:
            if random.random() < 0.1:  # 10% mutation chance
                avg_genes[gene] *= random.uniform(0.95, 1.05)
            avg_genes[gene] = max(0.5, min(1.5, avg_genes[gene]))
    else:
        avg_genes = self.queen.genes.copy()
    
    # Kill old queen, spawn new one
    self.queen = Queen(self.nest_pos[0], self.nest_pos[1], genes=avg_genes)
    self.queen.generation = self.queen.generation + 1
```

### **E. Pheromone Suppression (Immediate)**

**When new Queen spawns, she immediately suppresses worker reproduction:**

```python
def suppress_worker_reproduction(self):
    """New queen pheromone prevents worker reproduction"""
    # In a real sim, this would be pheromone-based
    # For MVP: just a flag that workers check
    self.queen_pheromone_active = True
```

**Workers check this when deciding to breed (if ever implemented):**
```python
if not sim.queen_pheromone_active:
    # Worker can reproduce
    pass
else:
    # Queen suppresses it
    pass
```

---

## Behavioral Integration

### **Pheromone Trails (Strong)**

**Fix trail-following to make pheromones matter:**

```python
# In ant.update()

# Get pheromone at current location
pheromone_strength = sim.get_pheromone_strength(self.x, self.y)

# HIGH sensitivity ants follow trails more strictly
if pheromone_strength > 20 * self.genes['sensitivity']:
    self.state = "follow_pheromone"
    # Move toward strongest pheromone nearby
    best_direction = sim.find_pheromone_gradient(self.x, self.y)
    if best_direction:
        self.x += best_direction[0] * self.actual_speed
        self.y += best_direction[1] * self.actual_speed
elif pheromone_strength > 5:
    # Weak trail detected, might follow
    if random.random() < self.genes['sensitivity']:
        self.state = "follow_pheromone"
else:
    # No trail, wander or seek food
    self.state = "wander"

# Trails reinforce when successful
if self.carrying_food and self.state == "return_nest":
    # Lay strong pheromone on return (success reinforcement)
    pheromone_strength_to_emit = 100
else:
    pheromone_strength_to_emit = 30
```

**Add helper function to find pheromone gradient:**

```python
def find_pheromone_gradient(self, x, y):
    """Find direction of strongest nearby pheromone"""
    # Check 8 directions
    best_strength = 0
    best_direction = None
    
    for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
        check_x = x + dx * 20
        check_y = y + dy * 20
        
        if 0 <= check_x < 800 and 0 <= check_y < 600:
            strength = self.get_pheromone_strength(check_x, check_y)
            if strength > best_strength:
                best_strength = strength
                best_direction = (dx, dy)
    
    return best_direction
```

---

## Rendering Updates

### **Show Royal Jelly**

```python
# In render.py, stats display
royal_jelly_text = f"Royal Jelly: {sim.royal_jelly}"
screen.blit(font.render(royal_jelly_text, True, (255, 200, 100)), (10, 100))
```

### **Show Emergency Mode**

```python
if sim.emergency_queen_mode:
    emergency_text = f"EMERGENCY: Raising new Queen..."
    screen.blit(font.render(emergency_text, True, (255, 0, 0)), (10, 120))
```

### **Food nodes** (from Phase 2B)
- Continue showing with depleting amounts
- Visually darker as depleted

---

## Tunable Parameters (in constants.py)

```python
QUEEN_DEATH_CHANCE_PER_GEN = 0.05  # 5% per generation
FOOD_TO_ROYAL_JELLY_RATIO = 30     # 30 food = 1 royal jelly
EMERGENCY_QUEEN_DEV_TIME = 240     # Frames to develop new queen
ROYAL_JELLY_PER_LARVA = 1          # Royal jelly cost per queen rearing
```

---

## Implementation Steps

### **Step 1: Queen mortality** (30 min)
- Add `alive` flag to Queen
- Implement `check_mortality()`
- Test: queen dies, flag triggers

### **Step 2: Royal jelly resource** (30 min)
- Add `royal_jelly` counter to Simulation
- Implement royal jelly generation (food → royal jelly conversion)
- Test: food drops, royal jelly increases

### **Step 3: Emergency queen development** (1.5 hours)
- Implement `update_emergency_queen()`
- Track development time
- Consume royal jelly during development
- Test: emergency mode triggers, develops over time

### **Step 4: New queen birth** (1 hour)
- Implement `spawn_new_queen()`
- New queen inherits blended worker genes
- Replace old queen with new queen
- Test: new queen spawns, colony continues

### **Step 5: Pheromone trail strengthening** (1 hour)
- Modify pheromone emission: successful returns emit more
- Modify ant behavior: follow strong trails preferentially
- Add `find_pheromone_gradient()` helper
- Test: ants follow trails better, trails reinforce

### **Step 6: Rendering** (1 hour)
- Show royal jelly in stats
- Show emergency mode warning
- Show pheromone strength visually (optional: brighter trails)

### **Step 7: Tuning** (1.5 hours)
- Run 5-10 simulations, vary `QUEEN_DEATH_CHANCE_PER_GEN`
- Adjust `EMERGENCY_QUEEN_DEV_TIME` to ~16 days equivalent
- Adjust `FOOD_TO_ROYAL_JELLY_RATIO` so costs are realistic
- Document optimal values

---

## Acceptance Criteria

✅ Queen can die (random, tunable chance)  
✅ When queen dies, emergency mode triggers  
✅ Food converts to royal jelly  
✅ Royal jelly feeds developing queen larva  
✅ After development time, new queen emerges  
✅ New queen immediately suppresses alternatives  
✅ New queen has blended genes from workers  
✅ Pheromone trails reinforce on successful returns  
✅ Ants strongly prefer high-concentration trails  
✅ Colony survives queen death and continues  
✅ Stats show royal jelly, emergency mode, queen status  
✅ Multiple simulations show stable colony recovery  

---

## Success Checkpoint (60 seconds)

**You run it and observe:**
- Queen alive, laying eggs
- Workers forage, follow pheromone trails
- Food depletes, new food spawns
- At some point: Queen dies (if death_chance triggered)
- Immediately: "EMERGENCY: Raising new Queen..." appears
- Food converts to royal jelly
- After ~240 frames: new queen emerges
- Colony continues growing

**Terminal output shows:**
```
Frame 300  | FPS: 60.2 | Ants: 12 | Food: 25 | Storage: 5 | RJ: 0 | QGen: 0 | Alive: Yes
Frame 600  | FPS: 59.9 | Ants: 14 | Food: 45 | Storage: 0 | RJ: 1 | QGen: 0 | Alive: No (EMERGENCY)
Frame 900  | FPS: 60.1 | Ants: 14 | Food: 60 | Storage: 3 | RJ: 0 | QGen: 1 | Alive: Yes (NEW)
```

**If successful:** Colony faces real mortality pressure. You can run 10 simulations and tune parameters to find values where colonies reliably survive.

---

## What NOT to Do

- ❌ Don't add multiple simultaneous queens yet
- ❌ Don't add queen fights
- ❌ Don't add swarming
- ❌ Don't add male ants (drones)

---

## Hand-off

**When done:**
1. Run `python main.py` for 60 seconds
2. Show **screenshot** (stats showing royal jelly, emergency mode if triggered)
3. Show **terminal output** with all stats
4. Run **5 simulations** (60 seconds each), document:
   - Did queen die?
   - Did colony recover?
   - What were final ant count, food, generations?
5. **Tuning report:**
   - What `QUEEN_DEATH_CHANCE_PER_GEN` made colonies most stable?
   - How many frames for queen development felt right?
   - What was optimal food → royal jelly cost?

**Required proof:**
- Working colony with queen mortality and recovery
- Terminal showing multiple metrics
- 5 simulation runs with outcomes documented

---

**Directive Created:** April 14, 2026  
**Target Completion:** Today/tomorrow  
**Owner:** Robert (rfd62794)
