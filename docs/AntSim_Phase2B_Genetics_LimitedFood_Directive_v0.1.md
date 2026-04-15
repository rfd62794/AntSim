# AntSim Phase 2B — Lifespan + Energy Efficiency + Limited Food
**For:** IDE Pair Programming Agent  
**Status:** Ready to execute  
**Timeline:** 5-7 hours  
**Language:** Python 3.10+  
**Framework:** Pygame 2.x (extending Phase 2A codebase)  

---

## Objective

1. Add 2 new genes to ants: **Lifespan** and **Energy Efficiency**
2. Implement **limited food supply** — each food node depletes when collected
3. When all food at a location is gone, respawn new food elsewhere on map
4. Watch colony adapt to scarcity pressure while genetics shift

---

## Core Changes

### **A. Food Node Structure**

**Replace simple food sources with persistent Food objects:**

```python
class FoodNode:
    def __init__(self, x, y, amount=10):
        self.x = x
        self.y = y
        self.amount = amount  # Finite supply (10 units)
        self.max_amount = amount
        self.active = True
    
    def take_food(self, quantity=1):
        """Remove food from this node"""
        if self.amount > 0:
            self.amount -= quantity
            if self.amount <= 0:
                self.active = False
            return 1
        return 0
    
    def is_depleted(self):
        return self.amount <= 0
```

**In Simulation:**

```python
class Simulation:
    def __init__(self):
        # ... existing code ...
        self.food_nodes = []
        
        # Spawn initial 5 food nodes with limited supply
        for _ in range(5):
            x = random.randint(100, 700)
            y = random.randint(100, 550)
            self.food_nodes.append(FoodNode(x, y, amount=10))
```

### **B. Food Respawn Logic**

**When a food node depletes, spawn new one elsewhere:**

```python
def check_food_respawn(self):
    """Remove depleted nodes, respawn new ones"""
    
    # Remove depleted nodes
    self.food_nodes = [fn for fn in self.food_nodes if not fn.is_depleted()]
    
    # If fewer than 5 active nodes, spawn new one
    if len(self.food_nodes) < 5:
        x = random.randint(100, 700)
        y = random.randint(100, 550)
        self.food_nodes.append(FoodNode(x, y, amount=10))

# Call in Simulation.update()
def update(self):
    # ... existing code ...
    self.check_food_respawn()
```

### **C. New Genes: Lifespan + Energy Efficiency**

**Extend Queen and Ant genes:**

```python
class Queen:
    def __init__(self, x, y, genes=None):
        # ... existing code ...
        if genes is None:
            self.genes = {
                'sensitivity': 1.0,
                'speed': 1.0,
                'boldness': 0.5,
                'lifespan': 1.0,           # NEW
                'energy_efficiency': 1.0   # NEW
            }
        else:
            self.genes = genes
```

```python
class Ant:
    def __init__(self, x, y, genes=None, queen_id=None):
        # ... existing code ...
        self.genes = genes or {
            'sensitivity': 1.0,
            'speed': 1.0,
            'boldness': 0.5,
            'lifespan': 1.0,
            'energy_efficiency': 1.0
        }
        
        # Lifespan: determines max energy before starvation
        self.max_energy = 100 * self.genes['lifespan']
        
        # Energy efficiency: multiplies energy drain rate
        self.energy_drain_rate = ANT_ENERGY_DRAIN / self.genes['energy_efficiency']
```

### **D. Gene Inheritance with Mutations**

**Update breed_ants() to handle 5 genes:**

```python
def breed_ants(queen, food_available):
    """Queen produces 1 worker with 5 genes + mutation"""
    
    if food_available >= 20:
        worker_genes = {}
        
        for gene in ['sensitivity', 'speed', 'boldness', 'lifespan', 'energy_efficiency']:
            base = queen.genes[gene]
            
            # Mutation: 5% chance to shift by ±5%
            if random.random() < 0.05:
                base *= random.uniform(0.95, 1.05)
            
            # Clamp to reasonable range
            worker_genes[gene] = max(0.5, min(1.5, base))
        
        worker = Ant(queen.x, queen.y, genes=worker_genes)
        queen.workers_born += 1
        
        return worker
    
    return None
```

### **E. Ant Behavior: Lifespan + Energy Efficiency**

**Lifespan affects survivability:**

```python
# In Ant.update()

# Energy drain varies by efficiency gene
self.energy -= self.energy_drain_rate

# Long-lived ants survive longer (high lifespan = high max_energy)
if self.energy <= 0:
    self.alive = False

# Energy regeneration when carrying food
if self.carrying_food:
    self.energy = min(self.max_energy, self.energy + ANT_ENERGY_GAIN)
```

**Energy efficiency affects foraging strategy:**

- High efficiency ants (need less food) can explore farther
- Low efficiency ants must return to food quickly or starve

```python
# In ant state transitions
if self.energy < self.max_energy * 0.3:
    # Low energy: prioritize return to nest
    self.state = "return_nest"
elif self.energy < self.max_energy * 0.6:
    # Medium energy: follow established trails (safe)
    if detected_pheromone > 10:
        self.state = "follow_pheromone"
```

### **F. Food Collection from Limited Nodes**

**When ant touches food node, consume from its supply:**

```python
# In Simulation.update(), collision detection
for ant in self.ants:
    for food_node in self.food_nodes:
        distance = math.sqrt((ant.x - food_node.x)**2 + (ant.y - food_node.y)**2)
        
        if distance < FOOD_RADIUS and not ant.carrying_food:
            # Take from limited supply
            if food_node.take_food(1):
                ant.carrying_food = True
                ant.state = "return_nest"
                break
```

### **G. Rendering Updates**

**Show food node depletion visually:**

```python
# In render.py
for food_node in sim.food_nodes:
    # Color brightness indicates remaining supply
    brightness = int(255 * (food_node.amount / food_node.max_amount))
    color = (0, brightness, 0)  # Green, brighter = more food
    
    pygame.draw.circle(screen, color, (int(food_node.x), int(food_node.y)), FOOD_RADIUS)
    
    # Draw amount text
    font_small = pygame.font.Font(None, 12)
    amount_text = font_small.render(str(food_node.amount), True, (255, 255, 255))
    screen.blit(amount_text, (int(food_node.x) - 5, int(food_node.y) - 5))
```

**Update stats display with new genes:**

```python
# Show Queen's current genes
sensitivity = f"{sim.queen.genes['sensitivity']:.2f}"
speed = f"{sim.queen.genes['speed']:.2f}"
boldness = f"{sim.queen.genes['boldness']:.2f}"
lifespan = f"{sim.queen.genes['lifespan']:.2f}"
efficiency = f"{sim.queen.genes['energy_efficiency']:.2f}"

gene_display = f"Sens:{sensitivity} Spd:{speed} Bold:{boldness} Life:{lifespan} Eff:{efficiency}"
screen.blit(font.render(gene_display, True, (255, 255, 255)), (10, 60))
```

---

## Implementation Steps

### **Step 1: Create FoodNode class** (30 min)
- Add FoodNode with amount tracking
- Implement take_food() and is_depleted()
- Test: create node, deplete it, verify is_depleted()

### **Step 2: Implement food respawn logic** (30 min)
- Add check_food_respawn() to Simulation
- Call in update()
- Test: deplete food, watch new node spawn elsewhere

### **Step 3: Add 2 new genes to Queen + Ant** (30 min)
- Add lifespan and energy_efficiency to Queen.genes and Ant.genes
- Implement max_energy and energy_drain_rate derived from genes
- Test: create ants with different genes, verify stats change

### **Step 4: Update breed_ants() for 5 genes** (30 min)
- Modify inheritance to handle all 5 genes
- Add mutation for each gene
- Test: breed ants, verify offspring have blended genes

### **Step 5: Integrate lifespan + efficiency into behavior** (1.5 hours)
- Ant.update() uses energy_drain_rate (modified by efficiency)
- Ant death when energy <= 0
- Energy regeneration when carrying food
- State transitions based on energy level
- Test: fast efficiency ants survive longer, slow ones die faster

### **Step 6: Food collection from limited nodes** (1 hour)
- Modify collision detection to deplete food_node.amount
- Verify food counter still increments correctly
- Test: collect from node, watch amount decrease

### **Step 7: Rendering + stats** (1 hour)
- Draw food nodes with brightness indicating supply
- Display amount text on nodes
- Update HUD to show all 5 genes
- Test: visual feedback matches game state

---

## Acceptance Criteria

✅ Food nodes spawn with limited amount (10 units each)  
✅ Ants can deplete food nodes (visually darker as depleted)  
✅ When all food at node consumed, node disappears  
✅ New food node spawns at random location  
✅ Always 5 active food nodes on map  
✅ Lifespan gene controls ant max_energy  
✅ Energy efficiency gene controls energy_drain_rate  
✅ High efficiency ants survive longer on same food  
✅ Low efficiency ants starve faster  
✅ Queen produces new generation with mutated genes  
✅ Colony adapts to food scarcity (genes shift to favor efficiency)  
✅ Stats display all 5 genes in real-time  
✅ Runs 60 FPS for 5+ minutes without crash  

---

## Success Checkpoint

**You run it and observe (60 seconds):**
- Queen spawned, visible
- 5 food nodes visible, with amounts displayed
- Ants deplete food (nodes get darker)
- Depleted nodes disappear, new ones spawn elsewhere
- Colony shrinks if food runs out (starvation pressure)
- Colony grows if food is plentiful
- Queen's genes shift over generations (lifespan/efficiency increase if scarcity pressure exists)
- Stats show all 5 genes updating

**Terminal output shows:**
```
Frame 300  | FPS: 60.2 | Ants: 12 | Food: 25 | Storage: 5 | QGen: 2
           | Life: 1.00 | Eff: 1.05
Frame 600  | FPS: 59.9 | Ants: 14 | Food: 45 | Storage: 0 | QGen: 4
           | Life: 1.02 | Eff: 1.12
Frame 900  | FPS: 60.1 | Ants: 16 | Food: 60 | Storage: 3 | QGen: 6
           | Life: 1.03 | Eff: 1.18
```

**If successful:** Colony now faces real scarcity. You can watch genes evolve in response.

---

## What NOT to Do

- ❌ Don't add predators yet
- ❌ Don't add UI to manually move food
- ❌ Don't add multiple Queens
- ❌ Don't add soldier/scout coding (let roles emerge)

---

## Hand-off

**When done:**
1. Run `python main.py` for 60 seconds
2. Show **screenshot** at 60s (food nodes visible with amounts, Queen present, colony size)
3. Show **terminal output** with all stats
4. Show **observation:** "Food depletes, new food spawns. Ants starve if efficiency is low. Gene adaptation visible in Queen genes."

**Required proof:**
- Screenshot showing depleted food node (darker green) and newly spawned node
- Terminal showing Queen's lifespan and efficiency genes changing over generations
- Actual working simulation, not summaries

---

**Directive Created:** April 14, 2026  
**Target Completion:** Today/tomorrow  
**Owner:** Robert (rfd62794)
